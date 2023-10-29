#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include "resolverContext.h"
#include "resolverTokens.h"

#include "pxr/pxr.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"

#include <iostream>

PXR_NAMESPACE_USING_DIRECTIVE

PythonResolverContext::PythonResolverContext() {
    // Init
    this->LoadOrRefreshData();
}

PythonResolverContext::PythonResolverContext(const PythonResolverContext& ctx) = default;

PythonResolverContext::PythonResolverContext(const std::string& mappingFilePath)
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context\n", mappingFilePath.c_str());
    // Init
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->LoadOrRefreshData();
}

bool
PythonResolverContext::operator<(
    const PythonResolverContext& ctx) const
{
    // This is a no-op for now, as it doesn't get used for now.
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


void PythonResolverContext::LoadOrRefreshData(){
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::LoadOrRefreshData('%s', '%s', '%s', '%s') - Loading data\n", this->GetMappingFilePath().c_str(), DEFINE_STRING(AR_ENV_SEARCH_PATHS), DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION), DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));
    std::string pythonResult;    
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "ResolverContext.LoadOrRefreshData",
                                     &pythonResult, this->GetMappingFilePath(), DEFINE_STRING(AR_ENV_SEARCH_PATHS),
                                     DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION), DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));  
    if (!state) {
        std::cerr << "Failed to call ResolverContext.LoadOrRefreshData in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::LoadOrRefreshData('%s') - Loaded data '%s'\n", this->GetMappingFilePath().c_str(), pythonResult.c_str());
    this->SetData(pythonResult);
}