#ifndef AR_HYBRIDRESOLVER_TOKENS_H
#define AR_HYBRIDRESOLVER_TOKENS_H

#include <vector>

#include <pxr/pxr.h>
#include <pxr/base/tf/staticTokens.h>

#include "api.h"

PXR_NAMESPACE_OPEN_SCOPE

struct FileResolverTokensType
{
    AR_HYBRIDRESOLVER_API FileResolverTokensType();

    const TfToken mappingPairs;
    const std::vector<TfToken> allTokens;
};

extern AR_HYBRIDRESOLVER_API TfStaticData<FileResolverTokensType> FileResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_HYBRIDRESOLVER_TOKENS_H