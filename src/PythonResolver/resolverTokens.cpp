#include "resolverTokens.h"

PXR_NAMESPACE_OPEN_SCOPE

PythonResolverTokensType::PythonResolverTokensType() :
    mappingPairs("mappingPairs", TfToken::Immortal),
    mappingRegexExpression("mappingRegexExpression", TfToken::Immortal),
    mappingRegexFormat("mappingRegexFormat", TfToken::Immortal),
    searchPaths("searchPaths", TfToken::Immortal),
    allTokens({
        mappingPairs,
        mappingRegexExpression,
        mappingRegexFormat,
        searchPaths
    })
{
}

TfStaticData<PythonResolverTokensType> PythonResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE
