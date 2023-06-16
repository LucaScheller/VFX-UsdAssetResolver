#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include <iostream>

#include "pxr/pxr.h"
#include "pxr/base/tf/error.h"
#include "pxr/base/tf/errorMark.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"

#include "resolverContext.h"
#include "resolverTokens.h"

PXR_NAMESPACE_USING_DIRECTIVE

PythonResolverContext::PythonResolverContext() = default;

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
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::LoadOrRefreshData('%s')\n", this->GetMappingFilePath().c_str());
    std::string pythonResult;
    
    TfErrorMark errorMark;
    errorMark.SetMark();           
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "ResolverContext.LoadOrRefreshData",
                                     &pythonResult, this->GetMappingFilePath());
    errorMark.SetMark();  
    if (!state) {
        for(TfError err: errorMark){
            std::cout << err.GetErrorCodeAsString() << std::endl;
        }
    }
    std::cout << state << std::endl;
    this->SetData(pythonResult);
}