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

FileResolverContext::FileResolverContext() {
    // Init
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(const FileResolverContext& ctx) = default;

FileResolverContext::FileResolverContext(const std::string& mappingFilePath)
{
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context\n", mappingFilePath.c_str());
    // Init
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

FileResolverContext::FileResolverContext(const std::vector<std::string>& searchPaths)
{
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext() - Creating new context with custom search paths\n");
    // Init
    this->_LoadEnvMappingRegex();
    this->SetCustomSearchPaths(searchPaths);
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(const std::string& mappingFilePath, const std::vector<std::string>& searchPaths)
{
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context with custom search paths\n", mappingFilePath.c_str());
    // Init
    this->_LoadEnvMappingRegex();
    this->SetCustomSearchPaths(searchPaths);
    this->RefreshSearchPaths();
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

bool
FileResolverContext::operator<(
    const FileResolverContext& ctx) const
{
    // This is a no-op for now, as it doesn't get used for now.
    return true;
}

bool
FileResolverContext::operator==(
    const FileResolverContext& ctx) const
{
    return this->GetMappingFilePath() == ctx.GetMappingFilePath();
}

bool
FileResolverContext::operator!=(
    const FileResolverContext& ctx) const
{
    return this->GetMappingFilePath() != ctx.GetMappingFilePath();
}

size_t hash_value(const FileResolverContext& ctx)
{
    return TfHash()(ctx.GetMappingFilePath());
}

void
FileResolverContext::_LoadEnvMappingRegex()
{
    data->mappingRegexExpressionStr = TfGetenv(DEFINE_STRING(AR_ENV_SEARCH_REGEX_EXPRESSION));
    data->mappingRegexExpression = std::regex(data->mappingRegexExpressionStr);
    data->mappingRegexFormat = TfGetenv(DEFINE_STRING(AR_ENV_SEARCH_REGEX_FORMAT));
}

void
FileResolverContext::_LoadEnvSearchPaths()
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

bool FileResolverContext::_GetMappingPairsFromUsdFile(const std::string& filePath)
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
    auto mappingDataPtr = layerMetaData.GetValueAtPath(FileResolverTokens->mappingPairs);
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

void FileResolverContext::AddMappingPair(const std::string& sourceStr, const std::string& targetStr){
    auto map_find = data->mappingPairs.find(sourceStr);
    if(map_find != data->mappingPairs.end()){
        map_find->second = targetStr;
    }else{
        data->mappingPairs.insert(std::pair<std::string, std::string>(sourceStr,targetStr));
    }
}

void FileResolverContext::RemoveMappingByKey(const std::string& sourceStr){
    const auto &it = data->mappingPairs.find(sourceStr);
    if (it != data->mappingPairs.end()){
        data->mappingPairs.erase(it);
    }
}

void FileResolverContext::RemoveMappingByValue(const std::string& targetStr){
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

void FileResolverContext::RefreshSearchPaths(){
    data->searchPaths.clear();
    this->_LoadEnvSearchPaths();
    if (!data->envSearchPaths.empty()) {
        data->searchPaths.insert(data->searchPaths.end(), data->envSearchPaths.begin(), data->envSearchPaths.end());
    }
    if (!data->customSearchPaths.empty()) {
        data->searchPaths.insert(data->searchPaths.end(), data->customSearchPaths.begin(), data->customSearchPaths.end());
    }
}

void FileResolverContext::SetCustomSearchPaths(const std::vector<std::string>& searchPaths){
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

void FileResolverContext::RefreshFromMappingFilePath(){
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

