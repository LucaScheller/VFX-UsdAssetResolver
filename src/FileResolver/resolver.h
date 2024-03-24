#ifndef AR_FILERESOLVER_RESOLVER_H
#define AR_FILERESOLVER_RESOLVER_H

#include "api.h"
#include "debugCodes.h"
#include "resolverContext.h"

#include "pxr/pxr.h"
#include "pxr/usd/ar/resolver.h"

#include <memory>
#include <string>
#include <map>

PXR_NAMESPACE_OPEN_SCOPE

struct FileResolverContextRecord
{
    ArTimestamp timestamp;
    FileResolverContext ctx;
};

static std::map<std::string, FileResolverContextRecord> _sharedContexts;

class FileResolver final : public ArResolver
{
public:
    AR_FILERESOLVER_API
    FileResolver();

    AR_FILERESOLVER_API
    virtual ~FileResolver();

    AR_FILERESOLVER_API
    bool GetExposeAbsolutePathIdentifierState(){ return this->exposeAbsolutePathIdentifierState; }
    AR_FILERESOLVER_API
    void SetExposeAbsolutePathIdentifierState(const bool state){
        if (state != this->exposeAbsolutePathIdentifierState){
            this->exposeAbsolutePathIdentifierState = state;
        }
    }

protected:
    AR_FILERESOLVER_API
    std::string _CreateIdentifier(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_FILERESOLVER_API
    std::string _CreateIdentifierForNewAsset(
        const std::string& assetPath,
        const ArResolvedPath& anchorAssetPath) const final;

    AR_FILERESOLVER_API
    ArResolvedPath _Resolve(
        const std::string& assetPath) const final;

    AR_FILERESOLVER_API
    ArResolvedPath _ResolveForNewAsset(
        const std::string& assetPath) const final;

    AR_FILERESOLVER_API
    ArResolverContext _CreateDefaultContext() const final;

    AR_FILERESOLVER_API
    ArResolverContext _CreateDefaultContextForAsset(
        const std::string& assetPath) const final; 

    AR_FILERESOLVER_API
    bool _IsContextDependentPath(
        const std::string& assetPath) const final;

    AR_FILERESOLVER_API
    void _RefreshContext(
        const ArResolverContext& context) final;

    AR_FILERESOLVER_API
    ArTimestamp _GetModificationTimestamp(
        const std::string& assetPath,
        const ArResolvedPath& resolvedPath) const final;

    AR_FILERESOLVER_API
    std::shared_ptr<ArAsset> _OpenAsset(
        const ArResolvedPath& resolvedPath) const final;

    AR_FILERESOLVER_API
    std::shared_ptr<ArWritableAsset> _OpenAssetForWrite(
        const ArResolvedPath& resolvedPath,
        WriteMode writeMode) const final;
    
private:
    const FileResolverContext* _GetCurrentContextPtr() const;
    FileResolverContext _fallbackContext;
    bool exposeAbsolutePathIdentifierState{false};
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_H