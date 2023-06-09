#ifndef AR_FILERESOLVER_RESOLVER_H
#define AR_FILERESOLVER_RESOLVER_H

#include <memory>
#include <string>

#include "pxr/pxr.h"
#include "pxr/usd/ar/asset.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolver.h"
#include "pxr/usd/ar/resolvedPath.h"
#include "pxr/usd/ar/resolverContext.h"
#include "pxr/usd/ar/writableAsset.h"
#include "pxr/base/vt/value.h"

#include "resolverContext.h"

PXR_NAMESPACE_OPEN_SCOPE

class FileResolver final : public ArResolver
{
public:
    AR_API
    FileResolver();

    AR_API
    virtual ~FileResolver();

protected:
    AR_API
    std::string _CreateIdentifier(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_API
    std::string _CreateIdentifierForNewAsset(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_API
    ArResolvedPath _Resolve(
        const std::string& assetPath) const final;

    AR_API
    ArResolvedPath _ResolveForNewAsset(
        const std::string& assetPath) const final;

    AR_API
    ArResolverContext _CreateDefaultContext() const final;

    AR_API
    ArResolverContext _CreateDefaultContextForAsset(
        const std::string& assetPath) const final;

    AR_API
    ArResolverContext _CreateContextFromString(
        const std::string& contextStr) const final;

    AR_API
    bool _IsContextDependentPath(
        const std::string& assetPath) const final;

    AR_API
    void _RefreshContext(
        const ArResolverContext& context) final;

    AR_API
    ArTimestamp _GetModificationTimestamp(
        const std::string& assetPath,
        const ArResolvedPath& resolvedPath) const final;

    AR_API
    std::shared_ptr<ArAsset> _OpenAsset(
        const ArResolvedPath& resolvedPath) const final;

    AR_API
    std::shared_ptr<ArWritableAsset> _OpenAssetForWrite(
        const ArResolvedPath& resolvedPath,
        WriteMode writeMode) const final;
    
private:
    const FileResolverContext* _GetCurrentContextPtr() const;
    
    FileResolverContext _fallbackContext;
    ArResolverContext _defaultContext;
};

PXR_NAMESPACE_CLOSE_SCOPE


#endif // AR_FILERESOLVER_RESOLVER_H