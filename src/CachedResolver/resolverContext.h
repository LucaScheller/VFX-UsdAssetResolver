#ifndef AR_CACHEDRESOLVER_RESOLVER_CONTEXT_H
#define AR_CACHEDRESOLVER_RESOLVER_CONTEXT_H

#include "api.h"
#include "debugCodes.h"

#include "pxr/pxr.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include <memory>
#include <regex>
#include <string>
#include <map>

/* Data Model
We use an internal data struct that is accessed via a shared pointer
as Usd currently creates resolver context copies when exposed via python
instead of passing thru the pointer. This way we can send
> ArNotice::ResolverChanged(*ctx).Send();
notifications to the stages.
> See for more info: https://groups.google.com/g/usd-interest/c/9JrXGGbzBnQ/m/_f3oaqBdAwAJ
*/
struct CachedResolverContextInternalData
{
    std::string mappingFilePath;
    std::map<std::string, std::string> mappingPairs;
    std::map<std::string, std::string> cachedPairs;
};

class CachedResolverContext
{
public:
    // Constructors
    AR_CACHEDRESOLVER_API
    CachedResolverContext();
    AR_CACHEDRESOLVER_API
    CachedResolverContext(const CachedResolverContext& ctx);
    AR_CACHEDRESOLVER_API
    CachedResolverContext(const std::string& mappingFilePath);
    
    // Standard Ops
    AR_CACHEDRESOLVER_API
    bool operator<(const CachedResolverContext& ctx) const;
    AR_CACHEDRESOLVER_API
    bool operator==(const CachedResolverContext& ctx) const;
    AR_CACHEDRESOLVER_API
    bool operator!=(const CachedResolverContext& ctx) const;
    AR_CACHEDRESOLVER_API
    friend size_t hash_value(const CachedResolverContext& ctx);

    // Methods
    AR_CACHEDRESOLVER_API
    const std::string& GetMappingFilePath() const { return data->mappingFilePath;}
    AR_CACHEDRESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { data->mappingFilePath = mappingFilePath; }
    AR_CACHEDRESOLVER_API
    void RefreshFromMappingFilePath();
    AR_CACHEDRESOLVER_API
    void AddMappingPair(const std::string& sourceStr, const std::string& targetStr);
    AR_CACHEDRESOLVER_API
    void RemoveMappingByKey(const std::string& sourceStr);
    AR_CACHEDRESOLVER_API
    void RemoveMappingByValue(const std::string& targetStr);
    AR_CACHEDRESOLVER_API
    const std::map<std::string, std::string>& GetMappingPairs() const { return data->mappingPairs; }
    AR_CACHEDRESOLVER_API
    void ClearMappingPairs() { data->mappingPairs.clear(); }
    AR_CACHEDRESOLVER_API
    void AddCachingPair(const std::string& sourceStr, const std::string& targetStr);
    AR_CACHEDRESOLVER_API
    void RemoveCachingByKey(const std::string& sourceStr);
    AR_CACHEDRESOLVER_API
    void RemoveCachingByValue(const std::string& targetStr);
    AR_CACHEDRESOLVER_API
    const std::map<std::string, std::string>& GetCachingPairs() const { return data->cachedPairs; }
    AR_CACHEDRESOLVER_API
    void ClearCachingPairs() { data->cachedPairs.clear(); }
    AR_CACHEDRESOLVER_API
    const std::string ResolveAndCachePair(const std::string& assetPath) const;

private:
    // Vars
    std::shared_ptr<CachedResolverContextInternalData> data = std::make_shared<CachedResolverContextInternalData>();
    std::string emptyString{""};
    // Methods
    bool _GetMappingPairsFromUsdFile(const std::string& filePath);
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(CachedResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_CACHEDRESOLVER_RESOLVER_CONTEXT_H