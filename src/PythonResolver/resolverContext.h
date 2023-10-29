#ifndef AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H
#define AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H

#include "api.h"
#include "debugCodes.h"

#include "pxr/pxr.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include <memory>
#include <regex>
#include <string>


/* Data Model
We use an internal data struct that is accessed via a shared pointer
as Usd currently creates resolver context copies when exposed via python
instead of passing thru the pointer. This way we can send
> ArNotice::ResolverChanged(*ctx).Send();
notifications to the stages.
> See for more info: https://groups.google.com/g/usd-interest/c/9JrXGGbzBnQ/m/_f3oaqBdAwAJ
*/

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
    const std::string& GetMappingFilePath() const { return *_mappingFilePath;}
    AR_PYTHONRESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { *_mappingFilePath = mappingFilePath; }
    AR_PYTHONRESOLVER_API
    void LoadOrRefreshData();
    AR_PYTHONRESOLVER_API
    const std::string GetData() const { return *_data; }
    AR_PYTHONRESOLVER_API
    void SetData(std::string data) { *_data = data; }
private:
    // Vars
    std::shared_ptr<std::string> _mappingFilePath = std::make_shared<std::string>();
    std::shared_ptr<std::string> _data = std::make_shared<std::string>();
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(PythonResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_PYTHONRESOLVER_RESOLVER_CONTEXT_H