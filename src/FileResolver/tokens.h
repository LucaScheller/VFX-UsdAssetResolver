#ifndef AR_FILERESOLVER_TOKENS_H
#define AR_FILERESOLVER_TOKENS_H

#include <vector>

#include <pxr/pxr.h>
#include <pxr/base/tf/staticTokens.h>
#include <pxr/usd/ar/api.h>

PXR_NAMESPACE_OPEN_SCOPE

struct FileResolverTokensType {
    AR_API FileResolverTokensType();

    const TfToken mappingPairs;
    const std::vector<TfToken> allTokens;
};


extern AR_API TfStaticData<FileResolverTokensType> FileResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_TOKENS_H