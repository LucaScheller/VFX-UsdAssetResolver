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
    for (int i; i < array.size(); i++)
    {
        if (getStringEndswithString(value, array[i]))
        {
            return true;
        }
    }
    return false;
}

PythonResolverContext::PythonResolverContext() {
    // Init
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
}

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

PythonResolverContext::PythonResolverContext(const std::vector<std::string>& searchPaths)
{
    // Init
    this->_LoadEnvMappingRegex();
    this->SetCustomSearchPaths(searchPaths);
    this->RefreshSearchPaths();
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::ResolverContext() -  Creating new context with custom search paths\n");
}

PythonResolverContext::PythonResolverContext(const std::string& mappingFilePath, const std::vector<std::string>& searchPaths)
{
    // Init
    this->_LoadEnvMappingRegex();
    this->SetCustomSearchPaths(searchPaths);
    this->RefreshSearchPaths();
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::ResolverContext('%s') -  Creating new context with custom search paths\n", mappingFilePath.c_str());
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

void
PythonResolverContext::_LoadEnvMappingRegex()
{
    data->mappingRegexExpressionStr = TfGetenv(DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION));
    data->mappingRegexExpression = std::regex(data->mappingRegexExpressionStr);
    data->mappingRegexFormat = TfGetenv(DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));
}

void
PythonResolverContext::_LoadEnvSearchPaths()
{
    data->envSearchPaths.clear();
    const std::string envSearchPathsStr = TfGetenv(DEFINE_STRING(AR_ENV_SEARCH_PATHS));
    if (!envSearchPathsStr.empty()) {
        const std::vector<std::string> envSearchPaths = TfStringTokenize(envSearchPathsStr, ARCH_PATH_LIST_SEP);
        for (const std::string& envSearchPath : envSearchPaths) {
            if (envSearchPath.empty()) { continue; }
            const std::string absEnvSearchPath = TfAbsPath(envSearchPath);
            if (absEnvSearchPath.empty()) {
                TF_WARN(
                    "Could not determine absolute path for search path prefix "
                    "'%s'", envSearchPath.c_str());
                continue;
            }
            data->envSearchPaths.push_back(absEnvSearchPath);
        }
    }
}

bool PythonResolverContext::_GetMappingPairsFromUsdFile(const std::string& filePath)
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
    auto mappingDataPtr = layerMetaData.GetValueAtPath(PythonResolverTokens->mappingPairs);
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

void PythonResolverContext::AddMappingPair(const std::string& sourceStr, const std::string& targetStr){
    if (data->mappingPairs.count(sourceStr)){
        data->mappingPairs[sourceStr] = targetStr;
    }else{
        data->mappingPairs.insert(std::pair<std::string, std::string>(sourceStr,targetStr));
    }
}

void PythonResolverContext::RemoveMappingByKey(const std::string& sourceStr){
    const auto &it = data->mappingPairs.find(sourceStr);
    if (it != data->mappingPairs.end()){
        data->mappingPairs.erase(it);
    }
}

void PythonResolverContext::RemoveMappingByValue(const std::string& targetStr){
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

