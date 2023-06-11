#include "resolverTokens.h"

PXR_NAMESPACE_OPEN_SCOPE

PythonResolverTokensType::PythonResolverTokensType() :
    mappingPairs("mappingPairs", TfToken::Immortal),
    allTokens({
        mappingPairs
    })
{
}

TfStaticData<PythonResolverTokensType> PythonResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE
