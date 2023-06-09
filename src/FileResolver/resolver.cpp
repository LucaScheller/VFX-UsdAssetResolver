#include <fstream>
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <unordered_map>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include "pxr/pxr.h"
#include "pxr/usd/ar/assetInfo.h"
#include "pxr/usd/ar/defineResolver.h"
#include "pxr/usd/ar/filesystemAsset.h"
#include "pxr/usd/ar/filesystemWritableAsset.h"
#include "pxr/usd/ar/notice.h"
#include "pxr/base/js/json.h"
#include "pxr/base/js/value.h"
#include "pxr/base/tf/debug.h"
#include "pxr/base/tf/diagnostic.h"
#include "pxr/base/tf/envSetting.h"
#include "pxr/base/tf/fileUtils.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/base/tf/stl.h"
#include "pxr/base/tf/stringUtils.h"
#include "pxr/base/vt/dictionary.h"
#include "pxr/base/arch/fileSystem.h"
#include "pxr/base/arch/systemInfo.h"

#include "resolver.h"
#include "resolverContext.h"


PXR_NAMESPACE_USING_DIRECTIVE
namespace python = AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(FileResolver, ArResolver);

TF_DEBUG_CODES(
    USD_RESOLVER_EXAMPLE
);

TF_DEFINE_ENV_SETTING(
    USD_RESOLVER_EXAMPLE_ASSET_DIR, ".",
    "Root of asset directory used by FileResolver.")


PXR_NAMESPACE_CLOSE_SCOPE


static bool
_IsFileRelative(const std::string& path) {
    return path.find("./") == 0 || path.find("../") == 0;
}

static bool
_IsRelativePath(const std::string& path)
{
    return (!path.empty() && TfIsRelativePath(path));
}

static bool
_IsSearchPath(const std::string& path)
{
    return _IsRelativePath(path) && !_IsFileRelative(path);
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
    const std::string anchoredPath = TfStringCatPaths(
        TfStringGetBeforeSuffix(forwardPath, '/'), path);
    return TfNormPath(anchoredPath);
}



static std::vector<std::string>
_ParseSearchPaths(const std::string& pathStr)
{
    return TfStringTokenize(pathStr, ARCH_PATH_LIST_SEP);
}

static TfStaticData<std::vector<std::string>> _SearchPath;

FileResolver::FileResolver()
{
    std::vector<std::string> searchPath = *_SearchPath;
    const std::string envPath = TfGetenv("PXR_AR_DEFAULT_SEARCH_PATH");
    if (!envPath.empty()) {
        const std::vector<std::string> envSearchPath = 
            _ParseSearchPaths(envPath);
        searchPath.insert(
            searchPath.end(), envSearchPath.begin(), envSearchPath.end());
    }

    //_fallbackContext = ArDefaultResolverContext(searchPath);
}

FileResolver::~FileResolver() = default;

std::vector<std::string>
FileResolver::GetDefaultSearchPaths()
{
    return *_SearchPath;
}

void
FileResolver::SetDefaultSearchPaths(
    const std::vector<std::string>& searchPath)
{
    *_SearchPath = searchPath;
}


std::string
FileResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg("FileResolver::_CreateIdentifier('%s', '%s')\n",
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
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
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
        // XXX - CLEANUP:
        // It's tempting to use AnchorRelativePath to combine the two
        // paths here, but that function's file-relative anchoring
        // causes consumers to break. 
        // 
        // Ultimately what we should do is specify whether anchorPath 
        // in both Resolve and _AnchorRelativePath can be files or directories 
        // and fix up all the callers to accommodate this.
        resolvedPath = TfStringCatPaths(anchorPath, path);
    }

    // Use TfAbsPath to ensure we return an absolute path using the
    // platform-specific representation (e.g. '\' as path separators
    // on Windows.
    return TfPathExists(resolvedPath) ?
        ArResolvedPath(TfAbsPath(resolvedPath)) : ArResolvedPath();
}



ArResolvedPath
FileResolver::_Resolve(
    const std::string& assetPath) const
{

    std::cout << "Resolving " << assetPath << std::endl;
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
    
    return ArResolvedPath(TfAbsPath("/opt/hfs19.5/houdini/usd/assets/pig/pig.usd"));
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::_Resolve('%s')\n",
        assetPath.c_str());
    if (assetPath.empty()) {
        return ArResolvedPath();
    }

    if (_IsRelativePath(assetPath)) {
        // First try to resolve relative paths against the current
        // working directory.


        


        

        ArResolvedPath resolvedPath = _ResolveAnchored(ArchGetCwd(), assetPath);
        if (resolvedPath) {
            return resolvedPath;
        }

        return _ResolveAnchored(std::string(), assetPath);
    }

    return _ResolveAnchored(std::string(), assetPath);
}

ArResolvedPath
FileResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::_ResolveForNewAsset('%s')\n",
        assetPath.c_str());
    return ArResolvedPath(assetPath.empty() ? assetPath : TfAbsPath(assetPath));
}

ArResolverContext
FileResolver::_CreateDefaultContext() const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::_CreateDefaultContext()\n");

    const std::string defaultMappingFile = TfAbsPath("versions.json");
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Looking for default mapping at %s...", defaultMappingFile.c_str());

    return ArResolverContext();
}

ArResolverContext
FileResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::_CreateDefaultContextForAsset('%s')\n",
        assetPath.c_str());

    const std::string assetDir = TfGetPathName(assetPath);
    const std::string mappingFile = 
        TfAbsPath(TfStringCatPaths(assetDir, "versions.json"));

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Looking for mapping at %s...", mappingFile.c_str());

    if (TfIsFile(mappingFile)) {
        TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" found\n");
        return ArResolverContext(
            FileResolverContext(mappingFile));
    }

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" not found\n");
    return ArResolverContext();
}

ArResolverContext
FileResolver::_CreateContextFromString(
    const std::string& contextStr) const
{
    // This resolver assumes the given context string will be a path to a
    // mapping file. This allows client code to call
    // ArGetResolver()->CreateContextFromString("asset", <filepath>) to create a
    // FileResolverContext without having to link against this
    // library directly.
    if (TfIsFile(contextStr)) {
        return ArResolverContext(
            FileResolverContext(contextStr));
    }

    return ArResolverContext();
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
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExample::_RefreshContext()\n");

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
}

ArTimestamp
FileResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::GetModificationTimestamp(resolvedPath);
}

std::shared_ptr<ArAsset>
FileResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());

    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
FileResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "FileResolver::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));

    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}