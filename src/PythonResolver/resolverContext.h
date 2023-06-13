#ifndef AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H
#define AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H

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
struct PythonResolverContextInternalData
{
    std::vector<std::string> searchPaths;
    std::vector<std::string> envSearchPaths;
    std::vector<std::string> customSearchPaths;
    std::string mappingFilePath;
    std::map<std::string, std::string> mappingPairs;
    std::regex mappingRegexExpression;
    std::string mappingRegexExpressionStr;
    std::string mappingRegexFormat;
};

class PythonResolverContext
{
public:
    // Constructors
    PythonResolverContext();
    AR_PYTHONRESOLVER_API
    PythonResolverContext(const PythonResolverContext& ctx);
    AR_PYTHONRESOLVER_API
    PythonResolverContext(const std::string& mappingFilePath);

    // Standard Ops
    AR_PYTHONRESOLVER_API
    bool operator<(const PythonResolverContext& ctx) const;
    AR_PYTHONRESOLVER_API
    bool operator==(const PythonResolverContext& ctx) const;
    AR_PYTHONRESOLVER_API
    bool operator!=(const PythonResolverContext& ctx) const;
    AR_PYTHONRESOLVER_API
    friend size_t hash_value(const PythonResolverContext& ctx);

    // Methods
    AR_PYTHONRESOLVER_API
    const std::string& GetMappingFilePath() const { return data->mappingFilePath;}
    AR_PYTHONRESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { data->mappingFilePath = mappingFilePath; }
    AR_PYTHONRESOLVER_API
    void RefreshFromMappingFilePath();
    AR_PYTHONRESOLVER_API
    const std::map<std::string, std::string>& GetMappingPairs() const { return data->mappingPairs; }

private:
    // Vars
    std::shared_ptr<std::string> data = std::make_shared<std::string>();
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(PythonResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H