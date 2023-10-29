#ifndef AR_PYTHONRESOLVER_RESOLVER_H
#define AR_PYTHONRESOLVER_RESOLVER_H

#include "api.h"
#include "debugCodes.h"
#include "resolverContext.h"

#include "pxr/pxr.h"
#include "pxr/usd/ar/resolver.h"

#include <memory>
#include <string>
#include <map>

PXR_NAMESPACE_OPEN_SCOPE

struct PythonResolverContextRecord
{
    ArTimestamp timestamp;
    PythonResolverContext ctx;
};

static std::map<std::string, PythonResolverContextRecord> _sharedContexts;

class PythonResolver final : public ArResolver
{
public:
    AR_PYTHONRESOLVER_API
    PythonResolver();

    AR_PYTHONRESOLVER_API
    virtual ~PythonResolver();

protected:
    AR_PYTHONRESOLVER_API
    std::string _CreateIdentifier(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_PYTHONRESOLVER_API
    std::string _CreateIdentifierForNewAsset(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_PYTHONRESOLVER_API
    ArResolvedPath _Resolve(
        const std::string& assetPath) const final;

    AR_PYTHONRESOLVER_API
    ArResolvedPath _ResolveForNewAsset(
        const std::string& assetPath) const final;

    AR_PYTHONRESOLVER_API
    ArResolverContext _CreateDefaultContext() const final;

    AR_PYTHONRESOLVER_API
    ArResolverContext _CreateDefaultContextForAsset(
        const std::string& assetPath) const final; 

    AR_PYTHONRESOLVER_API
    bool _IsContextDependentPath(
        const std::string& assetPath) const final;

    AR_PYTHONRESOLVER_API
    void _RefreshContext(
        const ArResolverContext& context) final;

    AR_PYTHONRESOLVER_API
    ArTimestamp _GetModificationTimestamp(
        const std::string& assetPath,
        const ArResolvedPath& resolvedPath) const final;

    AR_PYTHONRESOLVER_API
    std::shared_ptr<ArAsset> _OpenAsset(
        const ArResolvedPath& resolvedPath) const final;

    AR_PYTHONRESOLVER_API
    std::shared_ptr<ArWritableAsset> _OpenAssetForWrite(
        const ArResolvedPath& resolvedPath,
        WriteMode writeMode) const final;
    
private:
    const PythonResolverContext* _GetCurrentContextPtr() const;
    PythonResolverContext _fallbackContext;
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_PYTHONRESOLVER_RESOLVER_H