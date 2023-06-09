#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)

#include "pxr/pxr.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/arch/fileSystem.h"
#include "pxr/base/arch/systemInfo.h"
#include "pxr/usd/ar/assetInfo.h"
#include "pxr/usd/ar/defineResolver.h"
#include "pxr/usd/ar/filesystemAsset.h"
#include "pxr/usd/ar/filesystemWritableAsset.h"
#include "pxr/usd/ar/notice.h"
#include "pxr/base/js/json.h"
#include "pxr/base/js/value.h"
#include "pxr/base/tf/debug.h"
#include "pxr/base/tf/diagnostic.h"
#include "pxr/base/tf/envSetting.h"
#include "pxr/base/tf/fileUtils.h"
#include "pxr/base/tf/getenv.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/base/tf/stl.h"
#include "pxr/base/tf/stringUtils.h"
#include "pxr/base/vt/dictionary.h"

#include "resolverContext.h"

PXR_NAMESPACE_OPEN_SCOPE

FileResolverContext::FileResolverContext() {
    // Init
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(
    const FileResolverContext&) = default;

FileResolverContext::FileResolverContext(const std::string& mappingFilePath) : _mappingFilePath(TfAbsPath(mappingFilePath))
{
    // Init
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(const std::vector<std::string>& searchPaths)
{
    // Init
    this->SetCustomSearchPaths(searchPaths); // This refreshes automatically
}

bool
FileResolverContext::operator<(
    const FileResolverContext& ctx) const
{
    return _mappingFilePath < ctx._mappingFilePath;
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

const std::string& 
FileResolverContext::GetMappingFilePath() const
{
    return _mappingFilePath;
}

std::vector<std::string> FileResolverContext::GetSearchPaths(){
    return _searchPaths;
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

std::vector<std::string> FileResolverContext::GetEnvSearchPaths(){
    return _envSearchPaths;
}

std::vector<std::string> FileResolverContext::GetCustomSearchPaths(){
    return _customSearchPaths;
}

void FileResolverContext::SetCustomSearchPaths(const std::vector<std::string>& searchPaths){
    _customSearchPaths.clear();
    if (!searchPaths.empty()) {
        _customSearchPaths.insert(_customSearchPaths.end(), searchPaths.begin(), searchPaths.end());
    }
    this->RefreshSearchPaths();
}

void
FileResolverContext::_LoadEnvSearchPaths()
{
    _envSearchPaths.clear();
    const std::string envSearchPathsStr = TfGetenv(DEFINE_STRING(AR_FILERESOLVER_ENV_SEARCH_PATHS));
    if (!envSearchPathsStr.empty()) {
        const std::vector<std::string> envSearchPaths = TfStringTokenize(envSearchPathsStr, ARCH_PATH_LIST_SEP);
        _envSearchPaths.insert(_envSearchPaths.end(), envSearchPaths.begin(), envSearchPaths.end());
    }
}

PXR_NAMESPACE_CLOSE_SCOPE