#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <regex>

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

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(PythonResolver, ArResolver);

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

PythonResolver::PythonResolver() = default;

PythonResolver::~PythonResolver() = default;

std::string
PythonResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("::_CreateIdentifier('%s', '%s')\n",
                                        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());

    std::string pythonResult;
    TfPyInvokeAndExtract("PythonExpose", "PythonResolver._CreateIdentifier", &pythonResult);
    return pythonResult;
}

std::string
PythonResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::_CreateIdentifierForNewAsset"
        "('%s', '%s')\n",
        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());
    std::string pythonResult;
    TfPyInvokeAndExtract("PythonExpose", "PythonResolver._CreateIdentifierForNewAsset", &pythonResult);
    return pythonResult;
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
PythonResolver::_Resolve(
    const std::string& assetPath) const
{
    if (assetPath.empty()) {
        return ArResolvedPath();
    }
    if (_IsRelativePath(assetPath)) {
        ArResolvedPath resolvedPath = _ResolveAnchored(ArchGetCwd(), assetPath);
        if (resolvedPath) {
            return resolvedPath;
        }
        if (this->_IsContextDependentPath(assetPath)) {
            const PythonResolverContext* contexts[2] = {this->_GetCurrentContextPtr(), &_fallbackContext};
            for (const PythonResolverContext* ctx : contexts) {
                if (ctx) {
                    std::string mappedPath = assetPath;
                    if (!ctx->GetMappingRegexExpressionStr().empty())
                    {
                        mappedPath = std::regex_replace(mappedPath,
                                                        ctx->GetMappingRegexExpression(),
                                                        ctx->GetMappingRegexFormat());

                         TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Mapped to '%s' via regex expression '%s' with formatting '%s'\n", assetPath.c_str(), mappedPath.c_str(), ctx->GetMappingRegexExpressionStr().c_str(), ctx->GetMappingRegexFormat().c_str());
                    }
                    auto mappingPairs = ctx->GetMappingPairs();
                    if (mappingPairs.count(mappedPath)){
                        mappedPath = mappingPairs[mappedPath];
                    }
                    for (const auto& searchPath : ctx->GetSearchPaths()) {
                        resolvedPath = _ResolveAnchored(searchPath, mappedPath);
                        if (resolvedPath) {
                            return resolvedPath;
                        }
                    }
                }
            }
        }
        return ArResolvedPath();
    }
    return _ResolveAnchored(std::string(), assetPath);
}

ArResolvedPath
PythonResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("::_ResolveForNewAsset('%s')\n", assetPath.c_str());
    return ArResolvedPath(assetPath.empty() ? assetPath : TfAbsPath(assetPath));
}

ArResolverContext
PythonResolver::_CreateDefaultContext() const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContext()\n");
    return _fallbackContext;
}

ArResolverContext
PythonResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    // As there can be only one context class instance per context class
    // we automatically skip creation of contexts if it exists (The performance heavy
    // part is the pinning data creation). Here we can return any existing instance of
    // a PythonResolverContext, thats why we just use the fallback context.
    // See for more info: https://openusd.org/release/api/class_ar_resolver_context.html
    // > Note that an ArResolverContext may not hold multiple context objects with the same type.
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s')\n", assetPath.c_str());
    // Fallback to existing context
    if (assetPath.empty()){
        return ArResolverContext(_fallbackContext);
    }
    ArResolvedPath resolvedPath = this->_Resolve(assetPath);
    if (!TfPathExists(resolvedPath)){
        return ArResolverContext(_fallbackContext);
    }
    std::string resolvedPathStr = resolvedPath.GetPathString();
    if(this->_GetCurrentContextObject<PythonResolverContext>() != nullptr){
        TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Skipping on same stage\n", assetPath.c_str());
        return ArResolverContext(_fallbackContext);
    }
    auto map_iter = _sharedContexts.find(resolvedPath);
    if(map_iter != _sharedContexts.end()){
        if (map_iter->second.timestamp.GetTime() == this->_GetModificationTimestamp(assetPath, resolvedPath).GetTime())
        {
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Reusing context on different stage\n", assetPath.c_str());
            return ArResolverContext(map_iter->second.ctx);
        }else{
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Reusing context on different stage, reloading due to changed timestamp\n", assetPath.c_str());
            map_iter->second.ctx.RefreshFromMappingFilePath();
            return ArResolverContext(map_iter->second.ctx);
        }
    }
    // Create new context
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Constructing new context\n", assetPath.c_str());
    std::string assetDir = TfGetPathName(TfAbsPath(resolvedPathStr));
    struct PythonResolverContextRecord record;
    record.timestamp = this->_GetModificationTimestamp(assetPath, resolvedPath);
    record.ctx = PythonResolverContext(resolvedPath, std::vector<std::string>(1, assetDir));;
    _sharedContexts.insert(std::pair<std::string, PythonResolverContextRecord>(resolvedPath, record));
    return ArResolverContext(record.ctx);
}

bool
PythonResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    return _IsSearchPath(assetPath);
}

void
PythonResolver::_RefreshContext(
    const ArResolverContext& context)
{


    const PythonResolverContext* ctx = this->_GetCurrentContextPtr();
    if (!ctx) {
        return;
    }
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_RefreshContext()\n");

    ArNotice::ResolverChanged(*ctx).Send();
}

ArTimestamp
PythonResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::GetModificationTimestamp(resolvedPath);
}

std::shared_ptr<ArAsset>
PythonResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());

    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
PythonResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));

    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}

const PythonResolverContext* 
PythonResolver::_GetCurrentContextPtr() const
{
    return _GetCurrentContextObject<PythonResolverContext>();
}

PXR_NAMESPACE_CLOSE_SCOPE