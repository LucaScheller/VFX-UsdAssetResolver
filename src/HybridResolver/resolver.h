#ifndef AR_HYBRIDRESOLVER_RESOLVER_H
#define AR_HYBRIDRESOLVER_RESOLVER_H

#include <memory>
#include <string>
#include <map>

#include "pxr/pxr.h"
#include "pxr/usd/ar/resolver.h"

#include "api.h"
#include "debugCodes.h"
#include "resolverContext.h"

PXR_NAMESPACE_OPEN_SCOPE

struct HybridResolverContextRecord
{
    ArTimestamp timestamp;
    HybridResolverContext ctx;
};

static std::map<std::string, HybridResolverContextRecord> _sharedContexts;

class HybridResolver final : public ArResolver
{
public:
    AR_HYBRIDRESOLVER_API
    HybridResolver();

    AR_HYBRIDRESOLVER_API
    virtual ~HybridResolver();

protected:
    AR_HYBRIDRESOLVER_API
    std::string _CreateIdentifier(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_HYBRIDRESOLVER_API
    std::string _CreateIdentifierForNewAsset(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_HYBRIDRESOLVER_API
    ArResolvedPath _Resolve(
        const std::string& assetPath) const final;

    AR_HYBRIDRESOLVER_API
    ArResolvedPath _ResolveForNewAsset(
        const std::string& assetPath) const final;

    AR_HYBRIDRESOLVER_API
    ArResolverContext _CreateDefaultContext() const final;

    AR_HYBRIDRESOLVER_API
    ArResolverContext _CreateDefaultContextForAsset(
        const std::string& assetPath) const final; 

    AR_HYBRIDRESOLVER_API
    bool _IsContextDependentPath(
        const std::string& assetPath) const final;

    AR_HYBRIDRESOLVER_API
    void _RefreshContext(
        const ArResolverContext& context) final;

    AR_HYBRIDRESOLVER_API
    ArTimestamp _GetModificationTimestamp(
        const std::string& assetPath,
        const ArResolvedPath& resolvedPath) const final;

    AR_HYBRIDRESOLVER_API
    std::shared_ptr<ArAsset> _OpenAsset(
        const ArResolvedPath& resolvedPath) const final;

    AR_HYBRIDRESOLVER_API
    std::shared_ptr<ArWritableAsset> _OpenAssetForWrite(
        const ArResolvedPath& resolvedPath,
        WriteMode writeMode) const final;
    
private:
    const HybridResolverContext* _GetCurrentContextPtr() const;
    HybridResolverContext _fallbackContext;
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_HYBRIDRESOLVER_RESOLVER_H