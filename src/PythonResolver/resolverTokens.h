#ifndef AR_PYTHONRESOLVER_TOKENS_H
#define AR_PYTHONRESOLVER_TOKENS_H

#include <vector>

#include <pxr/pxr.h>
#include <pxr/base/tf/staticTokens.h>

#include "api.h"

PXR_NAMESPACE_OPEN_SCOPE

struct PythonResolverTokensType
{
    AR_PYTHONRESOLVER_API PythonResolverTokensType();

    const TfToken mappingPairs;
    const TfToken mappingRegexExpression;
    const TfToken mappingRegexFormat;
    const TfToken searchPaths;
    const std::vector<TfToken> allTokens;
};

extern AR_PYTHONRESOLVER_API TfStaticData<PythonResolverTokensType> PythonResolverTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_PYTHONRESOLVER_TOKENS_H