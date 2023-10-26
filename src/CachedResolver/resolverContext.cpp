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


CachedResolverContext::CachedResolverContext() {
    // Init
    this->LoadOrRefreshData();
}

CachedResolverContext::CachedResolverContext(const CachedResolverContext& ctx) = default;

CachedResolverContext::CachedResolverContext(const std::string& mappingFilePath)
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context\n", mappingFilePath.c_str());
    // Init
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->LoadOrRefreshData();
}

bool
CachedResolverContext::operator<(
    const CachedResolverContext& ctx) const
{
    // This is a no-op for now, as it doesn't get used for now.
    return true;
}

bool
CachedResolverContext::operator==(
    const CachedResolverContext& ctx) const
{
    return this->GetMappingFilePath() == ctx.GetMappingFilePath();
}

bool
CachedResolverContext::operator!=(
    const CachedResolverContext& ctx) const
{
    return this->GetMappingFilePath() != ctx.GetMappingFilePath();
}

size_t hash_value(const CachedResolverContext& ctx)
{
    return TfHash()(ctx.GetMappingFilePath());
}


bool CachedResolverContext::_GetMappingPairsFromUsdFile(const std::string& filePath)
{
    data->mappingPairs.clear();
    std::vector<std::string> usdFilePathExts{ ".usd", ".usdc", ".usda" };
    if (!getStringEndswithStrings(filePath, usdFilePathExts))
    {
        return false;
    }
    auto layer = SdfLayer::FindOrOpen(TfAbsPath(filePath));
    if (!layer){
        return false;
    }
    auto layerMetaData = layer->GetCustomLayerData();
    auto mappingDataPtr = layerMetaData.GetValueAtPath(CachedResolverTokens->mappingPairs);
    if (!mappingDataPtr){
        return false;
    }
    pxr::VtStringArray mappingDataArray = mappingDataPtr->Get<pxr::VtStringArray>();
    if (mappingDataArray.size() % 2 != 0){
        return false;
    }
    for (size_t i = 0; i < mappingDataArray.size(); i+=2) {
        this->AddMappingPair(mappingDataArray[i], mappingDataArray[i+1]);
    }
    return true;
}


void CachedResolverContext::LoadOrRefreshData(){
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::LoadOrRefreshData('%s', '%s', '%s', '%s') - Loading data\n", this->GetMappingFilePath().c_str(), DEFINE_STRING(AR_ENV_SEARCH_PATHS), DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION), DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));
    std::string pythonResult;    
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "ResolverContext.LoadOrRefreshData",
                                     &pythonResult, this->GetMappingFilePath(), DEFINE_STRING(AR_ENV_SEARCH_PATHS),
                                     DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION), DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));  
    if (!state) {
        std::cerr << "Failed to call ResolverContext.LoadOrRefreshData in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::LoadOrRefreshData('%s') - Loaded data '%s'\n", this->GetMappingFilePath().c_str(), pythonResult.c_str());
    this->SetData(pythonResult);
}