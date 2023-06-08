#include <fstream>
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <unordered_map>

#include "../utils/boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include "pxr/pxr.h"

#include "resolver.h"
#include "resolverContext.h"

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
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/base/tf/stl.h"
#include "pxr/base/tf/stringUtils.h"
#include "pxr/base/vt/dictionary.h"
#include "pxr/base/arch/fileSystem.h"
#include "pxr/base/arch/systemInfo.h"



PXR_NAMESPACE_USING_DIRECTIVE
namespace python = BOOST_NAMESPACE::python;

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(UsdResolverExampleResolver, ArResolver);

TF_DEBUG_CODES(
    USD_RESOLVER_EXAMPLE
);

TF_DEFINE_ENV_SETTING(
    USD_RESOLVER_EXAMPLE_ASSET_DIR, ".",
    "Root of asset directory used by UsdResolverExampleResolver.")


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


UsdResolverExampleResolver::UsdResolverExampleResolver()
{
}

UsdResolverExampleResolver::~UsdResolverExampleResolver() = default;


std::string
UsdResolverExampleResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg("UsdResolverExampleResolver::_CreateIdentifier('%s', '%s')\n",
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
UsdResolverExampleResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_CreateIdentifierForNewAsset"
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
UsdResolverExampleResolver::_Resolve(
    const std::string& assetPath) const
{

    std::cout << "Resolving " << assetPath << std::endl;
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    // Call Python/C API functions...
    //pValue= PyObject_CallObject(pFunc, pArgs2);  Crash is always given here

    // >>> import MyPythonClass
    try {
        //Py_Initialize();
        python::object my_python_class_module = python::import("MyPythonClass");
        // >>> dog = MyPythonClass.Dog()
        python::object dog = my_python_class_module.attr("Dog")();
        // >>> dog.bark("woof");
        dog.attr("bark")("woof");
    }
    catch (...) {
        std::cout << "Access denied - You must be at least 18 years old.\n";
    }

    PyGILState_Release(gstate);

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_Resolve('%s')\n",
        assetPath.c_str());
    if (assetPath.empty()) {
        return ArResolvedPath();
    }

    if (_IsRelativePath(assetPath)) {
        // First try to resolve relative paths against the current
        // working directory.


        return ArResolvedPath(TfAbsPath("/opt/hfs19.5/houdini/usd/assets/pig/pig.usd"));


        

        ArResolvedPath resolvedPath = _ResolveAnchored(ArchGetCwd(), assetPath);
        if (resolvedPath) {
            return resolvedPath;
        }

        return _ResolveAnchored(std::string(), assetPath);
    }

    return _ResolveAnchored(std::string(), assetPath);
}

ArResolvedPath
UsdResolverExampleResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_ResolveForNewAsset('%s')\n",
        assetPath.c_str());
    return ArResolvedPath(assetPath.empty() ? assetPath : TfAbsPath(assetPath));
}

ArResolverContext
UsdResolverExampleResolver::_CreateDefaultContext() const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_CreateDefaultContext()\n");

    const std::string defaultMappingFile = TfAbsPath("versions.json");
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Looking for default mapping at %s...", defaultMappingFile.c_str());

    return ArResolverContext();
}

ArResolverContext
UsdResolverExampleResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_CreateDefaultContextForAsset('%s')\n",
        assetPath.c_str());

    const std::string assetDir = TfGetPathName(assetPath);
    const std::string mappingFile = 
        TfAbsPath(TfStringCatPaths(assetDir, "versions.json"));

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Looking for mapping at %s...", mappingFile.c_str());

    if (TfIsFile(mappingFile)) {
        TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" found\n");
        return ArResolverContext(
            UsdResolverExampleResolverContext(mappingFile));
    }

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" not found\n");
    return ArResolverContext();
}

ArResolverContext
UsdResolverExampleResolver::_CreateContextFromString(
    const std::string& contextStr) const
{
    // This resolver assumes the given context string will be a path to a
    // mapping file. This allows client code to call
    // ArGetResolver()->CreateContextFromString("asset", <filepath>) to create a
    // UsdResolverExampleResolverContext without having to link against this
    // library directly.
    if (TfIsFile(contextStr)) {
        return ArResolverContext(
            UsdResolverExampleResolverContext(contextStr));
    }

    return ArResolverContext();
}

bool
UsdResolverExampleResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    return _IsSearchPath(assetPath);
}

void
UsdResolverExampleResolver::_RefreshContext(
    const ArResolverContext& context)
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExample::_RefreshContext()\n");

    // If the given ArResolverContext isn't holding a context object
    // used by this resolver, there's nothing to do so we can exit.    
    const UsdResolverExampleResolverContext* ctx = 
        context.Get<UsdResolverExampleResolverContext>();
    if (!ctx) {
        return;
    }

    // Send notification that any asset resolution done with an
    // ArResolverContext holding an equivalent context object to
    // ctx has been invalidated.
    ArNotice::ResolverChanged(*ctx).Send();
}

ArTimestamp
UsdResolverExampleResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::GetModificationTimestamp(resolvedPath);
}

std::shared_ptr<ArAsset>
UsdResolverExampleResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());

    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
UsdResolverExampleResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));

    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}
