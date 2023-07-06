#include "resolverTokens.h"

PXR_NAMESPACE_OPEN_SCOPE

FileResolverTokensType::FileResolverTokensType() :
    mappingPairs("mappingPairs", TfToken::Immortal),
    allTokens({
        mappingPairs
    })
{
}

TfStaticData<FileResolverTokensType> FileResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE
