#include <pxr/base/tf/registryManager.h>

#include "debugCodes.h"

PXR_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfDebug)
{
    TF_DEBUG_ENVIRONMENT_SYMBOL(PYTHONRESOLVER_RESOLVER, "Print debug output during path resolution");
    TF_DEBUG_ENVIRONMENT_SYMBOL(PYTHONRESOLVER_RESOLVER_CONTEXT, "Print debug output during context creating and modification");
}

PXR_NAMESPACE_CLOSE_SCOPE
