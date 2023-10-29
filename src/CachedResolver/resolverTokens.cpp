#include "resolverTokens.h"

PXR_NAMESPACE_OPEN_SCOPE

CachedResolverTokensType::CachedResolverTokensType() :
    mappingPairs("mappingPairs", TfToken::Immortal),
    cachedPairs("cachedPairs", TfToken::Immortal),
    allTokens({
        mappingPairs
    })
{
}

TfStaticData<CachedResolverTokensType> CachedResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE
