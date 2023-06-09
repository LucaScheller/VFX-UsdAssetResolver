#ifndef AR_FILERESOLVER_RESOLVER_CONTEXT_H
#define AR_FILERESOLVER_RESOLVER_CONTEXT_H

#include "pxr/pxr.h"

#include "api.h"

#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include <string>

class UsdResolverExampleResolverContext
{
public:
    AR_FILERESOLVER_API
    explicit UsdResolverExampleResolverContext(
        const std::string& mappingFile);

    AR_FILERESOLVER_API
    UsdResolverExampleResolverContext();

    AR_FILERESOLVER_API
    UsdResolverExampleResolverContext(
        const UsdResolverExampleResolverContext& rhs);

    AR_FILERESOLVER_API
    bool operator<(const UsdResolverExampleResolverContext& rhs) const;

    AR_FILERESOLVER_API
    bool operator==(const UsdResolverExampleResolverContext& rhs) const;
    
    AR_FILERESOLVER_API
    friend size_t hash_value(const UsdResolverExampleResolverContext& ctx);

    AR_FILERESOLVER_API
    const std::string& GetMappingFile() const;

private:
    std::string _mappingFile;
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(UsdResolverExampleResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_CONTEXT_H