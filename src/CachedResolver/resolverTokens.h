#ifndef AR_CACHEDRESOLVER_TOKENS_H
#define AR_CACHEDRESOLVER_TOKENS_H

#include "api.h"

#include <pxr/pxr.h>
#include <pxr/base/tf/staticTokens.h>

#include <vector>

PXR_NAMESPACE_OPEN_SCOPE

struct CachedResolverTokensType
{
    AR_CACHEDRESOLVER_API CachedResolverTokensType();

    const TfToken mappingPairs;
    const TfToken cachedPairs;
    const std::vector<TfToken> allTokens;
};

extern AR_CACHEDRESOLVER_API TfStaticData<CachedResolverTokensType> CachedResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_CACHEDRESOLVER_TOKENS_H