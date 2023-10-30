#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include "resolverContext.h"
#include "resolverTokens.h"

#include "pxr/pxr.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"
#include <pxr/usd/sdf/layer.h>

#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

/*
Safety-wise we lock via a mutex when we don't have a cache hit.
In theory we probably don't need this, as our Python call does this anyway.
See the _Resolve method for more information.
*/
static std::mutex g_resolver_query_mutex;

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

void CachedResolverContext::RefreshFromMappingFilePath(){
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
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

void CachedResolverContext::AddCachingPair(const std::string& sourceStr, const std::string& targetStr){
    auto cache_find = data->cachedPairs.find(sourceStr);
    if(cache_find != data->cachedPairs.end()){
        cache_find->second = targetStr;
    }else{
        data->cachedPairs.insert(std::pair<std::string, std::string>(sourceStr,targetStr));
    }
}

void CachedResolverContext::RemoveCachingByKey(const std::string& sourceStr){
    const auto &it = data->cachedPairs.find(sourceStr);
    if (it != data->cachedPairs.end()){
        data->cachedPairs.erase(it);
    }
}

void CachedResolverContext::RemoveCachingByValue(const std::string& targetStr){
    for (auto it = data->cachedPairs.cbegin(); it != data->cachedPairs.cend();)
    {
        if (it->second == targetStr)
        {
            data->cachedPairs.erase(it++);
        }
        else
        {
            ++it;
        }
    }
}

const std::string CachedResolverContext::ResolveAndCachePair(const std::string& assetPath) const{
    std::string pythonResult;
    {
        /*
        We perform the resource/thread lock in the context itself to 
        allow for resolver multithreading with different contexts.
        Is this approach in general a hacky solution? Yes, we are circumventing C++'s
        'constants' mechanism by redirecting our queries into Python in which we 
        write-access our Resolver Context. This way we can modify our 'const' C++ read
        locked resolver context. While it works, be aware that potential side effects may occur.
        This allows us to populate multiple cachePairs to allow for batch loading.
        */
        const std::lock_guard<std::mutex> lock(g_resolver_query_mutex);

        TF_DEBUG(CACHEDRESOLVER_RESOLVER).Msg("ResolverContext::ResolveAndCachePair('%s')\n", assetPath.c_str());
        
        int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                         "ResolverContext.ResolveAndCache",
                                         &pythonResult, assetPath, this);
        if (!state) {
            std::cerr << "Failed to call Resolver.ResolveAndCache in " << DEFINE_STRING(AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
            std::cerr << "Please verify that the python code is valid!" << std::endl;
        }
    }
    return pythonResult;
}