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

FileResolverContext::FileResolverContext() {
    // Init
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(
    const FileResolverContext&) = default;

FileResolverContext::FileResolverContext(const std::string& mappingFilePath)
{
    // Init
    this->RefreshSearchPaths();
    _mappingFilePath = TfAbsPath(mappingFilePath);
    this->_GetMappingPairsFromUsdFile(_mappingFilePath);
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolverContext::FileResolverContext('%s') -  Creating new context\n", mappingFilePath.c_str());
}

FileResolverContext::FileResolverContext(const std::string& mappingFilePath, const std::vector<std::string>& searchPaths)
{
    // Init
    this->SetCustomSearchPaths(searchPaths); // This calls RefreshSearchPaths
    _mappingFilePath = TfAbsPath(mappingFilePath);
    this->_GetMappingPairsFromUsdFile(_mappingFilePath);
    TF_DEBUG(FILERESOLVER_RESOLVER_CONTEXT).Msg("FileResolverContext::FileResolverContext('%s') -  Creating new context with custom search paths\n", mappingFilePath.c_str());
}

FileResolverContext::FileResolverContext(const std::vector<std::string>& searchPaths)
{
    // Init
    this->SetCustomSearchPaths(searchPaths); // This calls RefreshSearchPaths
}

bool
FileResolverContext::operator<(
    const FileResolverContext& ctx) const
{
    // This is a no-op as a < compare can't be implemented.
    return true;
}

bool
FileResolverContext::operator==(
    const FileResolverContext& ctx) const
{
    return _mappingFilePath == ctx._mappingFilePath;
}

bool
FileResolverContext::operator!=(
    const FileResolverContext& ctx) const
{
    return _mappingFilePath != ctx._mappingFilePath;
}

size_t hash_value(const FileResolverContext& ctx)
{
    return TfHash()(ctx._mappingFilePath);
}


bool FileResolverContext::_GetMappingPairsFromUsdFile(const std::string& filePath)
{
    _mappingPairs.clear();
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
    if (_mappingPairs.count(sourceStr)){
        _mappingPairs[sourceStr] = targetStr;
    }else{
        _mappingPairs.insert(std::pair<std::string, std::string>(sourceStr,targetStr));
    }
}

void FileResolverContext::RefreshSearchPaths(){
    _searchPaths.clear();
    this->_LoadEnvSearchPaths();
    if (!_envSearchPaths.empty()) {
        _searchPaths.insert(_searchPaths.end(), _envSearchPaths.begin(), _envSearchPaths.end());
    }
    if (!_customSearchPaths.empty()) {
        _searchPaths.insert(_searchPaths.end(), _customSearchPaths.begin(), _customSearchPaths.end());
    }
}


void FileResolverContext::SetCustomSearchPaths(const std::vector<std::string>& searchPaths){
    _customSearchPaths.clear();
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
            _customSearchPaths.push_back(absSearchPath);
        }
    }
    this->RefreshSearchPaths();
}

void FileResolverContext::RefreshMapping(){
    this->_GetMappingPairsFromUsdFile(_mappingFilePath);
}

void
FileResolverContext::_LoadEnvSearchPaths()
{
    _envSearchPaths.clear();
    const std::string envSearchPathsStr = TfGetenv(DEFINE_STRING(AR_FILERESOLVER_ENV_SEARCH_PATHS));
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
            _envSearchPaths.push_back(absEnvSearchPath);
        }
    }
}
