#ifndef AR_HYBRIDRESOLVER_RESOLVER_CONTEXT_H
#define AR_HYBRIDRESOLVER_RESOLVER_CONTEXT_H

#include <memory>
#include <regex>
#include <string>

#include "pxr/pxr.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include "api.h"
#include "debugCodes.h"

/* Data Model
We use an internal data struct that is accessed via a shared pointer
as Usd currently creates resolver context copies when exposed via python
instead of passing thru the pointer. This way we can send
> ArNotice::ResolverChanged(*ctx).Send();
notifications to the stages.
> See for more info: https://groups.google.com/g/usd-interest/c/9JrXGGbzBnQ/m/_f3oaqBdAwAJ
*/
struct HybridResolverContextInternalData
{
    std::string mappingFilePath;
    std::map<std::string, std::string> mappingPairs;
};

class HybridResolverContext
{
public:
    // Constructors
    HybridResolverContext();
    AR_HYBRIDRESOLVER_API
    HybridResolverContext(const HybridResolverContext& ctx);
    AR_HYBRIDRESOLVER_API
    HybridResolverContext(const std::string& mappingFilePath);

    // Standard Ops
    AR_HYBRIDRESOLVER_API
    bool operator<(const HybridResolverContext& ctx) const;
    AR_HYBRIDRESOLVER_API
    bool operator==(const HybridResolverContext& ctx) const;
    AR_HYBRIDRESOLVER_API
    bool operator!=(const HybridResolverContext& ctx) const;
    AR_HYBRIDRESOLVER_API
    friend size_t hash_value(const HybridResolverContext& ctx);

    // Methods
    AR_HYBRIDRESOLVER_API
    const std::string& GetMappingFilePath() const { return data->mappingFilePath;}
    AR_HYBRIDRESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { data->mappingFilePath = mappingFilePath; }
    AR_HYBRIDRESOLVER_API
    const std::map<std::string, std::string>& GetMappingPairs() const { return data->mappingPairs; }
    AR_HYBRIDRESOLVER_API
    void ClearMappingPairs() { data->mappingPairs.clear(); }

private:
    // Vars
    std::shared_ptr<HybridResolverContextInternalData> data = std::make_shared<HybridResolverContextInternalData>();
    
    // Methods
    bool _GetMappingPairsFromUsdFile(const std::string& filePath);

};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(HybridResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_HYBRIDRESOLVER_RESOLVER_CONTEXT_H