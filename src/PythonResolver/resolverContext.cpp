#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include <iostream>

#include "pxr/pxr.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include <pxr/usd/sdf/layer.h>

#include "resolverContext.h"
#include "resolverTokens.h"

PXR_NAMESPACE_USING_DIRECTIVE

PythonResolverContext::PythonResolverContext() = default;

PythonResolverContext::PythonResolverContext(const PythonResolverContext& ctx) = default;

PythonResolverContext::PythonResolverContext(const std::string& mappingFilePath)
{
    // Init
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::ResolverContext('%s') -  Creating new context\n", mappingFilePath.c_str());
}

bool
PythonResolverContext::operator<(
    const PythonResolverContext& ctx) const
{
    // This is a no-op as a < compare can't be implemented.
    return true;
}

bool
PythonResolverContext::operator==(
    const PythonResolverContext& ctx) const
{
    return this->GetMappingFilePath() == ctx.GetMappingFilePath();
}

bool
PythonResolverContext::operator!=(
    const PythonResolverContext& ctx) const
{
    return this->GetMappingFilePath() != ctx.GetMappingFilePath();
}

size_t hash_value(const PythonResolverContext& ctx)
{
    return TfHash()(ctx.GetMappingFilePath());
}

void PythonResolverContext::RefreshSearchPaths(){
    data->searchPaths.clear();
    this->_LoadEnvSearchPaths();
    if (!data->envSearchPaths.empty()) {
        data->searchPaths.insert(data->searchPaths.end(), data->envSearchPaths.begin(), data->envSearchPaths.end());
    }
    if (!data->customSearchPaths.empty()) {
        data->searchPaths.insert(data->searchPaths.end(), data->customSearchPaths.begin(), data->customSearchPaths.end());
    }
}

void PythonResolverContext::SetCustomSearchPaths(const std::vector<std::string>& searchPaths){
    data->customSearchPaths.clear();
    if (!searchPaths.empty()) {
        for (const std::string& searchPath : searchPaths) {
            if (searchPath.empty()) { continue; }
            const std::string absSearchPath = TfAbsPath(searchPath);
            if (absSearchPath.empty()) {
                TF_WARN(
                    "Could not determine absolute path for search path prefix "
                    "'%s'", searchPath.c_str());
                continue;
            }
            data->customSearchPaths.push_back(absSearchPath);
        }
    }
}

void PythonResolverContext::RefreshFromMappingFilePath(){
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

