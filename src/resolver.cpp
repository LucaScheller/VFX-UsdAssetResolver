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

#include <fstream>
#include <iostream>
#include <shared_mutex>
#include <thread>
#include <unordered_map>

PXR_NAMESPACE_USING_DIRECTIVE

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(UsdResolverExampleResolver, ArResolver);

TF_DEBUG_CODES(
    USD_RESOLVER_EXAMPLE
);

TF_DEFINE_ENV_SETTING(
    USD_RESOLVER_EXAMPLE_ASSET_DIR, ".",
    "Root of asset directory used by UsdResolverExampleResolver.")


PXR_NAMESPACE_CLOSE_SCOPE


UsdResolverExampleResolver::UsdResolverExampleResolver()
{
}

UsdResolverExampleResolver::~UsdResolverExampleResolver() = default;


std::string
UsdResolverExampleResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_CreateIdentifier('%s', '%s')\n",
        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());

    return "/opt/hfs19.5/houdini/usd/assets/pig/pig.usd";
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

    return assetPath;
}



ArResolvedPath
UsdResolverExampleResolver::_Resolve(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_Resolve('%s')\n",
        assetPath.c_str());
    ArResolvedPath resolvedPath;
    return resolvedPath;
}

ArResolvedPath
UsdResolverExampleResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_ResolveForNewAsset('%s')\n",
        assetPath.c_str());
    ArResolvedPath resolvedPath;
    return resolvedPath;
}

ArResolverContext
UsdResolverExampleResolver::_CreateDefaultContext() const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::_CreateDefaultContext()\n");

    const std::string defaultMappingFile = TfAbsPath("versions.json");
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Looking for default mapping at %s...", defaultMappingFile.c_str());

    if (TfIsFile(defaultMappingFile)) {
        TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" found\n");
        return ArResolverContext(
            UsdResolverExampleResolverContext(defaultMappingFile));
    }
    
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(" not found\n");
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
    return true;
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

    std::string filesystemPath = "/opt/hfs19.5/houdini/usd/assets/pig/pig.usd";

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Getting timestamp for %s\n", filesystemPath.c_str());
    return ArFilesystemAsset::GetModificationTimestamp(
        ArResolvedPath(std::move(filesystemPath)));
}

ArAssetInfo
UsdResolverExampleResolver::_GetAssetInfo(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::GetAssetInfo('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());

    ArAssetInfo assetInfo;
    assetInfo.assetName = "someName";
    assetInfo.version = 1;
    assetInfo.resolverInfo = VtDictionary{
        {"filesystemPath", VtValue("/opt/hfs19.5/houdini/usd/assets/pig/pig.usd")}
    };

    return assetInfo;
}

std::shared_ptr<ArAsset>
UsdResolverExampleResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "UsdResolverExampleResolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());

    std::string filesystemPath = "/opt/hfs19.5/houdini/usd/assets/pig/pig.usd";

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Opening file at %s\n", filesystemPath.c_str());
    return ArFilesystemAsset::Open(
        ArResolvedPath(std::move(filesystemPath)));
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

    std::string filesystemPath = "/opt/hfs19.5/houdini/usd/assets/pig/pig.usd";

    TF_DEBUG(USD_RESOLVER_EXAMPLE).Msg(
        "  - Opening file for write at %s\n", filesystemPath.c_str());
    return ArFilesystemWritableAsset::Create(
        ArResolvedPath(std::move(filesystemPath)), writeMode);
}
