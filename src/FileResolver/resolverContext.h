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
    USDRESOLVEREXAMPLE_API
    explicit UsdResolverExampleResolverContext(
        const std::string& mappingFile);

    USDRESOLVEREXAMPLE_API
    UsdResolverExampleResolverContext();

    USDRESOLVEREXAMPLE_API
    UsdResolverExampleResolverContext(
        const UsdResolverExampleResolverContext& rhs);

    USDRESOLVEREXAMPLE_API
    bool operator<(const UsdResolverExampleResolverContext& rhs) const;

    USDRESOLVEREXAMPLE_API
    bool operator==(const UsdResolverExampleResolverContext& rhs) const;
    
    USDRESOLVEREXAMPLE_API
    friend size_t hash_value(const UsdResolverExampleResolverContext& ctx);

    USDRESOLVEREXAMPLE_API
    const std::string& GetMappingFile() const;

private:
    std::string _mappingFile;
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(UsdResolverExampleResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_CONTEXT_H