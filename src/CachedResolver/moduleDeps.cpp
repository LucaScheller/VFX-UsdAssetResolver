#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)
#include <vector>

#include "pxr/pxr.h"
#include "pxr/base/tf/registryManager.h"
#include "pxr/base/tf/scriptModuleLoader.h"
#include "pxr/base/tf/token.h"

PXR_NAMESPACE_OPEN_SCOPE

TF_REGISTRY_FUNCTION(TfScriptModuleLoader) {
    // List of direct dependencies for this library.
    const std::vector<TfToken> reqs = {
        TfToken("ar"),
        TfToken("arch"),
        TfToken("gf"),
        TfToken("sdf"),
        TfToken("tf"),
        TfToken("vt"),
    };
    
    TfScriptModuleLoader::GetInstance().RegisterLibrary(TfToken(DEFINE_STRING(AR_CACHEDRESOLVER_USD_PLUGIN_NAME)), 
                                                        TfToken(DEFINE_STRING(AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME)), reqs);
}

PXR_NAMESPACE_CLOSE_SCOPE