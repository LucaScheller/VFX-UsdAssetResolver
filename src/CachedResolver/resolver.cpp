#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include "resolver.h"
#include "resolverContext.h"

#include "pxr/base/arch/systemInfo.h"
#include "pxr/base/tf/fileUtils.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/base/tf/stringUtils.h"
#include "pxr/usd/sdf/layer.h"
#include "pxr/usd/ar/defineResolver.h"
#include "pxr/usd/ar/filesystemAsset.h"
#include "pxr/usd/ar/filesystemWritableAsset.h"
#include "pxr/usd/ar/notice.h"

#include <fstream>
#include <iostream>
#include <map>

#include <string>
#include <regex>



PXR_NAMESPACE_OPEN_SCOPE

namespace python = pxr_boost::python;

AR_DEFINE_RESOLVER(CachedResolver, ArResolver);

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
_IsNotFilePath(const std::string& path)
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

CachedResolver::CachedResolver() = default;

CachedResolver::~CachedResolver() = default;

std::string
CachedResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg("Resolver::_CreateIdentifier('%s', '%s')\n",
                                          assetPath.c_str(), anchorAssetPath.GetPathString().c_str());

    if (assetPath.empty()) {
        return assetPath;
    }

    if (!anchorAssetPath) {
        return TfNormPath(assetPath);
    }

    const std::string anchoredAssetPath = _AnchorRelativePath(anchorAssetPath, assetPath);

    if (_IsNotFilePath(assetPath) && Resolve(anchoredAssetPath).empty()) {
        return TfNormPath(assetPath);
    }

    return TfNormPath(anchoredAssetPath);
}

std::string
CachedResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg(
        "Resolver::_CreateIdentifierForNewAsset"
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

ArResolvedPath
CachedResolver::_Resolve(
    const std::string& assetPath) const
{
    if (assetPath.empty()) {
        return ArResolvedPath();
    }
    if (SdfLayer::IsAnonymousLayerIdentifier(assetPath)){
        return ArResolvedPath(assetPath);
    }
    if (_IsRelativePath(assetPath)) {
        if (this->_IsContextDependentPath(assetPath)) {
            const CachedResolverContext* contexts[2] = {this->_GetCurrentContextPtr(), &_fallbackContext};
            for (const CachedResolverContext* ctx : contexts) {
                if (ctx) {
                    // Search for mapping pairs
                    auto &mappingPairs = ctx->GetMappingPairs();
                    auto map_find = mappingPairs.find(assetPath);
                    if(map_find != mappingPairs.end()){
                        ArResolvedPath resolvedPath = _ResolveAnchored(this->emptyString, map_find->second);
                        return resolvedPath;
                        // Assume that a map hit is always valid.
                        // if (resolvedPath) {
                        //     return resolvedPath;
                        // }
                    }
                    // Search for cached pairs
                    auto &cachedPairs = ctx->GetCachingPairs();
                    auto cache_find = cachedPairs.find(assetPath);
                    if(cache_find != cachedPairs.end()){
                        ArResolvedPath resolvedPath = _ResolveAnchored(this->emptyString, cache_find->second);
                        return resolvedPath;
                        // Assume that a cache hit is always valid.
                        // if (resolvedPath) {
                        //     return resolvedPath;
                        // }
                    }
                    // Perform query if caches don't have a hit.
                    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg("Resolver::_Resolve('%s') -> No cache hit, switching to Python query\n", assetPath.c_str());
                    /*
                    We perform the resource/thread lock in the context itself to 
                    allow for resolver multithreading with different contexts.
                    See .ResolveAndCachePair for more information.
                    */
                    ArResolvedPath resolvedPath = _ResolveAnchored(this->emptyString, ctx->ResolveAndCachePair(assetPath));
                    if (resolvedPath) {
                        return resolvedPath;
                    }
                    // Only try the first valid context.
                    break;
                }
            }
        }
        return ArResolvedPath();
    }
    return _ResolveAnchored(std::string(), assetPath);
}

ArResolvedPath
CachedResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg("Resolver::_ResolveForNewAsset('%s')\n", assetPath.c_str());
    return ArResolvedPath(assetPath.empty() ? assetPath : TfAbsPath(assetPath));
}

ArResolverContext
CachedResolver::_CreateDefaultContext() const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContext()\n");
    return _fallbackContext;
}

ArResolverContext
CachedResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    // As there can be only one context class instance per context class
    // we automatically skip creation of contexts if it exists (The performance heavy
    // part is the pinning data creation). Here we can return any existing instance of
    // a CachedResolverContext, thats why we just use the fallback context.
    // See for more info: https://openusd.org/release/api/class_ar_resolver_context.html
    // > Note that an ArResolverContext may not hold multiple context objects with the same type.
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s')\n", assetPath.c_str());
    // Fallback to existing context
    if (assetPath.empty()){
        return ArResolverContext(_fallbackContext);
    }
    ArResolvedPath resolvedPath = this->_Resolve(assetPath);
    if (!TfPathExists(resolvedPath)){
        return ArResolverContext(_fallbackContext);
    }
    std::string resolvedPathStr = resolvedPath.GetPathString();
    if(this->_GetCurrentContextObject<CachedResolverContext>() != nullptr){
        TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Skipping on same stage\n", assetPath.c_str());
        return ArResolverContext(_fallbackContext);
    }
    auto map_iter = _sharedContexts.find(resolvedPath);
    if(map_iter != _sharedContexts.end()){
        if (map_iter->second.timestamp.GetTime() == this->_GetModificationTimestamp(assetPath, resolvedPath).GetTime())
        {
            TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage\n", assetPath.c_str());
            return ArResolverContext(map_iter->second.ctx);
        }else{
            TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage, reloading due to changed timestamp\n", assetPath.c_str());
            map_iter->second.ctx.RefreshFromMappingFilePath();
            return ArResolverContext(map_iter->second.ctx);
        }
    }
    // Create new context
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Constructing new context\n", assetPath.c_str());
    struct CachedResolverContextRecord record;
    record.timestamp = this->_GetModificationTimestamp(assetPath, resolvedPath);
    record.ctx = CachedResolverContext(resolvedPath);
    _sharedContexts.insert(std::pair<std::string, CachedResolverContextRecord>(resolvedPath, record));
    return ArResolverContext(record.ctx);
}

bool
CachedResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_IsContextDependentPath()\n");
    return _IsNotFilePath(assetPath);
}

void
CachedResolver::_RefreshContext(
    const ArResolverContext& context)
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_RefreshContext()\n");
    const CachedResolverContext* ctx = this->_GetCurrentContextPtr();
    if (!ctx) {
        return;
    }
    ArNotice::ResolverChanged(*ctx).Send();
}

ArTimestamp
CachedResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg(
        "Resolver::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::GetModificationTimestamp(resolvedPath);
}

std::shared_ptr<ArAsset>
CachedResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg(
        "Resolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
CachedResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg(
        "Resolver::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));
    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}

const CachedResolverContext* 
CachedResolver::_GetCurrentContextPtr() const
{
    return _GetCurrentContextObject<CachedResolverContext>();
}

PXR_NAMESPACE_CLOSE_SCOPE
