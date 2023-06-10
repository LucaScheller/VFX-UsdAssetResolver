#include <fstream>
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <unordered_map>
#include <string>
#include <map>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include "pxr/base/arch/systemInfo.h"
#include "pxr/base/tf/fileUtils.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/usd/ar/defineResolver.h"
#include "pxr/usd/ar/filesystemAsset.h"
#include "pxr/usd/ar/filesystemWritableAsset.h"
#include "pxr/usd/ar/notice.h"

#include "resolver.h"
#include "resolverContext.h"

namespace python = AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(FileResolver, ArResolver);

static bool
_IsRelativePath(const std::string& path)
{
    return (!path.empty() && TfIsRelativePath(path));
}

static bool
_IsFileRelativePath(const std::string& path) {
    return path.find("./") == 0 || path.find("../") == 0;
}

static bool
_IsSearchPath(const std::string& path)
{
    return _IsRelativePath(path) && !_IsFileRelativePath(path);
}

static std::string
_AnchorRelativePath(
    const std::string& anchorPath, 
    const std::string& path)
{
    if (TfIsRelativePath(anchorPath) ||
        !_IsRelativePath(path)) {
        return path;
    }
    // Ensure we are using forward slashes and not back slashes.
    std::string forwardPath = anchorPath;
    std::replace(forwardPath.begin(), forwardPath.end(), '\\', '/');

    // If anchorPath does not end with a '/', we assume it is specifying
    // a file, strip off the last component, and anchor the path to that
    // directory.
    const std::string anchoredPath = TfStringCatPaths(TfStringGetBeforeSuffix(forwardPath, '/'), path);
    return TfNormPath(anchoredPath);
}

FileResolver::FileResolver() = default;

FileResolver::~FileResolver() = default;

std::string
FileResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg("FileResolver::_CreateIdentifier('%s', '%s')\n",
                                        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());

    if (assetPath.empty()) {
        return assetPath;
    }

    if (!anchorAssetPath) {
        return TfNormPath(assetPath);
    }

    const std::string anchoredAssetPath = _AnchorRelativePath(anchorAssetPath, assetPath);

    if (_IsSearchPath(assetPath) && Resolve(anchoredAssetPath).empty()) {
        return TfNormPath(assetPath);
    }

    return TfNormPath(anchoredAssetPath);
}

std::string
FileResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg(
        "FileResolver::_CreateIdentifierForNewAsset"
        "('%s', '%s')\n",
        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());
    if (assetPath.empty()) {
        return assetPath;
    }

    if (_IsRelativePath(assetPath)) {
        return TfNormPath(anchorAssetPath ? 
            _AnchorRelativePath(anchorAssetPath, assetPath) :
            TfAbsPath(assetPath));
    }

    return TfNormPath(assetPath);
}

static ArResolvedPath
_ResolveAnchored(
    const std::string& anchorPath,
    const std::string& path)
{
    std::string resolvedPath = path;
    if (!anchorPath.empty()) {
        resolvedPath = TfStringCatPaths(anchorPath, path);
    }
    return TfPathExists(resolvedPath) ? ArResolvedPath(TfAbsPath(resolvedPath)) : ArResolvedPath();
}

ArResolvedPath
FileResolver::_Resolve(
    const std::string& assetPath) const
{
    /*
    if (!Py_IsInitialized()){Py_Initialize();}
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    // Call Python/C API functions...
    try {
        python::object my_python_class_module = python::import("MyPythonClass");
        python::object dog = my_python_class_module.attr("Dog")();
        dog.attr("bark")();
    }
    catch (...) {
        PyErr_Print();
        std::cout << "No implementation for '_Resolve' found\n";
    }
    PyGILState_Release(gstate);
    */
    TfPyInvoke("MyPythonClass", "bark");
    return _ResolveAnchored(std::string(), assetPath);
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg("FileResolver::_Resolve('%s')\n", assetPath.c_str());

    if (assetPath.empty()) {
        return ArResolvedPath();
    }
    if (_IsRelativePath(assetPath)) {
        ArResolvedPath resolvedPath = _ResolveAnchored(ArchGetCwd(), assetPath);
        if (resolvedPath) {
            return resolvedPath;
        }
        return ArResolvedPath();
        /*
        if (_IsSearchPath(assetPath)) {
            const FileResolverContext* contexts[2] = {_GetCurrentContextPtr(), &_fallbackContext};
            for (const FileResolverContext* ctx : contexts) {
                if (ctx) {
                    for (const auto& searchPath : ctx->GetSearchPaths()) {
                        resolvedPath = _ResolveAnchored(searchPath, assetPath);
                        if (resolvedPath) {
                            return resolvedPath;
                        }
                    }
                }
            }
        }
        return ArResolvedPath();
        */
    }
    return _ResolveAnchored(std::string(), assetPath);
}

ArResolvedPath
FileResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg("FileResolver::_ResolveForNewAsset('%s')\n", assetPath.c_str());
    return ArResolvedPath(assetPath.empty() ? assetPath : TfAbsPath(assetPath));
}

ArResolverContext
FileResolver::_CreateDefaultContext() const
{
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContext()\n");
    return _fallbackContext;
}

ArResolverContext
FileResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    // As there can be only one context class instance per context class
    // we automatically skip creation of contexts if it exists (The performance heavy
    // part is the pinning data creation). Here we can return any existing instance of
    // a FileResolverContext, thats why we just use the fallback context.
    // See for more info: https://openusd.org/release/api/class_ar_resolver_context.html
    // > Note that an ArResolverContext may not hold multiple context objects with the same type.
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContextForAsset('%s')\n", assetPath.c_str());
    // Fallback to existing context
    if (assetPath.empty()){
        return ArResolverContext(_fallbackContext);
    }
    ArResolvedPath resolvedPath = this->_Resolve(assetPath);
    std::string resolvedPathStr = resolvedPath.GetPathString();
    if(this->_GetCurrentContextObject<FileResolverContext>() != nullptr){
        TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContextForAsset('%s') - Skipping on same stage\n", assetPath.c_str());
        return ArResolverContext(_fallbackContext);
    }
    auto map_iter = _sharedContexts.find(resolvedPath);
    if(map_iter != _sharedContexts.end()){
        if (map_iter->second.timestamp.GetTime() == this->_GetModificationTimestamp(assetPath, resolvedPath).GetTime())
        {
            TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage\n", assetPath.c_str());
            return ArResolverContext(map_iter->second.ctx);
        }else{
            TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage, reloading due to changed timestamp\n", assetPath.c_str());
            map_iter->second.ctx.RefreshMapping();
            return ArResolverContext(map_iter->second.ctx);
        }
    }
    // Create new context
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolver::_CreateDefaultContextForAsset('%s') - Constructing new context\n", assetPath.c_str());
    std::string assetDir = TfGetPathName(TfAbsPath(resolvedPathStr));
    struct FileResolverContextRecord record;
    record.timestamp = this->_GetModificationTimestamp(assetPath, resolvedPath);
    record.ctx = FileResolverContext(resolvedPath, std::vector<std::string>(1, assetDir));;
    _sharedContexts.insert(std::pair<std::string, FileResolverContextRecord>(resolvedPath, record));
    return ArResolverContext(record.ctx);
}

bool
FileResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    return _IsSearchPath(assetPath);
}

void
FileResolver::_RefreshContext(
    const ArResolverContext& context)
{
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg(
        "UsdResolverExample::_RefreshContext()\n");

    /*
    // If the given ArResolverContext isn't holding a context object
    // used by this resolver, there's nothing to do so we can exit.    
    const FileResolverContext* ctx = 
        context.Get<FileResolverContext>();
    if (!ctx) {
        return;
    }

    // Send notification that any asset resolution done with an
    // ArResolverContext holding an equivalent context object to
    // ctx has been invalidated.
    ArNotice::ResolverChanged(*ctx).Send();
    */
}

ArTimestamp
FileResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg(
        "FileResolver::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::GetModificationTimestamp(resolvedPath);
}

std::shared_ptr<ArAsset>
FileResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg(
        "FileResolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());

    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
FileResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(FILERESOLVER_RESOLVER).Msg(
        "FileResolver::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));

    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}

const FileResolverContext* 
FileResolver::_GetCurrentContextPtr() const
{
    return _GetCurrentContextObject<FileResolverContext>();
}

PXR_NAMESPACE_CLOSE_SCOPE