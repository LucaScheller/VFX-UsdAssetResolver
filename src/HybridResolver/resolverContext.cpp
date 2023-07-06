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
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(const FileResolverContext& ctx) = default;

FileResolverContext::FileResolverContext(const std::string& mappingFilePath)
{
    TF_DEBUG(HYBRIDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context\n", mappingFilePath.c_str());
    // Init
    this->_LoadEnvMappingRegex();
    this->RefreshSearchPaths();
    this->SetMappingFilePath(TfAbsPath(mappingFilePath));
    this->_GetMappingPairsFromUsdFile(this->GetMappingFilePath());
}

FileResolverContext::FileResolverContext(const std::vector<std::string>& searchPaths)
{
    TF_DEBUG(HYBRIDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext() - Creating new context with custom search paths\n");
    // Init
    this->_LoadEnvMappingRegex();
    this->SetCustomSearchPaths(searchPaths);
    this->RefreshSearchPaths();
}

FileResolverContext::FileResolverContext(const std::string& mappingFilePath, const std::vector<std::string>& searchPaths)
{
    TF_DEBUG(HYBRIDRESOLVER_RESOLVER_CONTEXT).Msg("ResolverContext::ResolverContext('%s') - Creating new context with custom search paths\n", mappingFilePath.c_str());
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
