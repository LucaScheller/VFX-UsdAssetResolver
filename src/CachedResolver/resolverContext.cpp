#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include <iostream>
#include <vector>

#include "pxr/pxr.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include <pxr/usd/sdf/layer.h>

#include "resolverContext.h"
#include "resolverTokens.h"

PXR_NAMESPACE_USING_DIRECTIVE

bool getStringEndswithString(const std::string &value, const std::string &compareValue)
{
    if (compareValue.size() > value.size())
    {
        return false;
    }
    if (std::equal(compareValue.rbegin(), compareValue.rend(), value.rbegin()))
    {
        return true;
    }
    return false;
}

bool getStringEndswithStrings(const std::string &value, const std::vector<std::string> array)
{
    for (int i=0; i < array.size(); i++)
    {
        if (getStringEndswithString(value, array[i]))
        {
            return true;
        }
    }
    return false;
}

CachedResolverContext::CachedResolverContext() {}

CachedResolverContext::CachedResolverContext(const CachedResolverContext& ctx) = default;

CachedResolverContext::CachedResolverContext(const std::string& mappingFilePath)
{
    TF_DEBUG(CACHEDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context\n", mappingFilePath.c_str());
    // Init
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
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

void CachedResolverContext::AddMappingPair(const std::string& sourceStr, const std::string& targetStr){
    auto map_find = data->mappingPairs.find(sourceStr);
    if(map_find != data->mappingPairs.end()){
        map_find->second = targetStr;
    }else{
        data->mappingPairs.insert(std::pair<std::string, std::string>(sourceStr,targetStr));
    }
}

void CachedResolverContext::RemoveMappingByKey(const std::string& sourceStr){
    const auto &it = data->mappingPairs.find(sourceStr);
    if (it != data->mappingPairs.end()){
        data->mappingPairs.erase(it);
    }
}

void CachedResolverContext::RemoveMappingByValue(const std::string& targetStr){
    for (auto it = data->mappingPairs.cbegin(); it != data->mappingPairs.cend();)
    {
        if (it->second == targetStr)
        {
            data->mappingPairs.erase(it++);
        }
        else
        {
            ++it;
        }
    }
}

void CachedResolverContext::RefreshFromMappingFilePath(){
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

const std::string CachedResolverContext::ResolveAndCachePair(const std::string& assetPath) const{
                    // We perform the resource/thread lock in the context itself to allow for resolver multithreading with different contexts
                    // This can populate multiple cachePairs to allow for batch loading of a identifier cache
    std::string debug{"debug"};
    return debug;
}