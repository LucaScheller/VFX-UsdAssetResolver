#ifndef AR_CACHEDRESOLVER_RESOLVER_H
#define AR_CACHEDRESOLVER_RESOLVER_H

#include "api.h"
#include "debugCodes.h"
#include "resolverContext.h"

#include "pxr/pxr.h"
#include "pxr/usd/ar/resolver.h"

#include <memory>
#include <string>
#include <map>

PXR_NAMESPACE_OPEN_SCOPE

struct CachedResolverContextRecord
{
    ArTimestamp timestamp;
    CachedResolverContext ctx;
};

static std::map<std::string, CachedResolverContextRecord> _sharedContexts;

class CachedResolver final : public ArResolver
{
public:
    AR_CACHEDRESOLVER_API
    CachedResolver();

    AR_CACHEDRESOLVER_API
    virtual ~CachedResolver();

protected:
    AR_CACHEDRESOLVER_API
    std::string _CreateIdentifier(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_CACHEDRESOLVER_API
    std::string _CreateIdentifierForNewAsset(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_CACHEDRESOLVER_API
    ArResolvedPath _Resolve(
        const std::string& assetPath) const final;

    AR_CACHEDRESOLVER_API
    ArResolvedPath _ResolveForNewAsset(
        const std::string& assetPath) const final;

    AR_CACHEDRESOLVER_API
    ArResolverContext _CreateDefaultContext() const final;

    AR_CACHEDRESOLVER_API
    ArResolverContext _CreateDefaultContextForAsset(
        const std::string& assetPath) const final; 

    AR_CACHEDRESOLVER_API
    bool _IsContextDependentPath(
        const std::string& assetPath) const final;

    AR_CACHEDRESOLVER_API
    void _RefreshContext(
        const ArResolverContext& context) final;

    AR_CACHEDRESOLVER_API
    ArTimestamp _GetModificationTimestamp(
        const std::string& assetPath,
        const ArResolvedPath& resolvedPath) const final;

    AR_CACHEDRESOLVER_API
    std::shared_ptr<ArAsset> _OpenAsset(
        const ArResolvedPath& resolvedPath) const final;

    AR_CACHEDRESOLVER_API
    std::shared_ptr<ArWritableAsset> _OpenAssetForWrite(
        const ArResolvedPath& resolvedPath,
        WriteMode writeMode) const final;
    
private:
    const CachedResolverContext* _GetCurrentContextPtr() const;
    CachedResolverContext _fallbackContext;
    const std::string emptyString;
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_CACHEDRESOLVER_RESOLVER_H