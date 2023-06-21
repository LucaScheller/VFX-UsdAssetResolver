#define CONVERT_STRING(string) #string
#define DEFINE_STRING(string) CONVERT_STRING(string)
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <regex>

#include "pxr/base/arch/systemInfo.h"
#include "pxr/base/tf/fileUtils.h"
#include "pxr/base/tf/pathUtils.h"
#include "pxr/base/tf/pyInvoke.h"
#include "pxr/base/tf/staticTokens.h"
#include "pxr/usd/ar/defineResolver.h"
#include "pxr/usd/ar/filesystemAsset.h"
#include "pxr/usd/ar/filesystemWritableAsset.h"
#include "pxr/usd/ar/notice.h"
#include "pxr/usd/ar/timestamp.h"

#include "resolver.h"
#include "resolverContext.h"

namespace python = AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_OPEN_SCOPE

AR_DEFINE_RESOLVER(PythonResolver, ArResolver);

PythonResolver::PythonResolver() = default;

PythonResolver::~PythonResolver() = default;

std::string
PythonResolver::_CreateIdentifier(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    const PythonResolverContext* contexts[2] = {this->_GetCurrentContextPtr(), &_fallbackContext};
    std::string serializedContext = "";
    std::string serializedFallbackContext = _fallbackContext.GetData(); 
    if (contexts[0] != nullptr){serializedContext=this->_GetCurrentContextPtr()->GetData();}
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("Resolver::_CreateIdentifier('%s', '%s', '%s', '%s')\n",
                                          assetPath.c_str(), anchorAssetPath.GetPathString().c_str(),
                                          serializedContext.c_str(), serializedFallbackContext.c_str());
    std::string pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._CreateIdentifier",
                                     &pythonResult, assetPath, anchorAssetPath, serializedContext, serializedFallbackContext);
    if (!state) {
        std::cerr << "Failed to call Resolver._CreateIdentifier in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

std::string
PythonResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "Resolver::_CreateIdentifierForNewAsset ('%s', '%s')\n",
        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());
    std::string pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._CreateIdentifierForNewAsset",
                                     &pythonResult, assetPath, anchorAssetPath);
    if (!state) {
        std::cerr << "Failed to call Resolver._CreateIdentifierForNewAsset in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

ArResolvedPath
PythonResolver::_Resolve(
    const std::string& assetPath) const
{
    const PythonResolverContext* contexts[2] = {this->_GetCurrentContextPtr(), &_fallbackContext};
    std::string serializedContext = "";
    std::string serializedFallbackContext = _fallbackContext.GetData(); 
    if (contexts[0] != nullptr){serializedContext=this->_GetCurrentContextPtr()->GetData();}
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("Resolver::_Resolve('%s', '%s', '%s')\n", assetPath.c_str(),
                                          serializedContext.c_str(), serializedFallbackContext.c_str());
    ArResolvedPath pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._Resolve",
                                     &pythonResult, assetPath, serializedContext, serializedFallbackContext);
    if (!state) {
        std::cerr << "Failed to call Resolver._Resolve in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

ArResolvedPath
PythonResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("Resolver::_ResolveForNewAsset('%s')\n", assetPath.c_str());
    ArResolvedPath pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._ResolveForNewAsset",
                                     &pythonResult, assetPath);
    if (!state) {
        std::cerr << "Failed to call Resolver._ResolveForNewAsset in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

ArResolverContext
PythonResolver::_CreateDefaultContext() const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContext()\n");
    return _fallbackContext;
}

ArResolverContext
PythonResolver::_CreateDefaultContextForAsset(
    const std::string& assetPath) const
{
    // As there can be only one context class instance per context class
    // we automatically skip creation of contexts if it exists (The performance heavy
    // part is the pinning data creation). Here we can return any existing instance of
    // a PythonResolverContext, thats why we just use the fallback context.
    // See for more info: https://openusd.org/release/api/class_ar_resolver_context.html
    // > Note that an ArResolverContext may not hold multiple context objects with the same type.
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s')\n", assetPath.c_str());
    // Fallback to existing context
    if (assetPath.empty()){
        return ArResolverContext(_fallbackContext);
    }
    ArResolvedPath resolvedPath = this->_Resolve(assetPath);
    if (!TfPathExists(resolvedPath)){
        return ArResolverContext(_fallbackContext);
    }
    std::string resolvedPathStr = resolvedPath.GetPathString();
    if(this->_GetCurrentContextObject<PythonResolverContext>() != nullptr){
        TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Skipping on same stage\n", assetPath.c_str());
        return ArResolverContext(_fallbackContext);
    }
    auto map_iter = _sharedContexts.find(resolvedPath);
    if(map_iter != _sharedContexts.end()){
        if (map_iter->second.timestamp.GetTime() == this->_GetModificationTimestamp(assetPath, resolvedPath).GetTime())
        {
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage\n", assetPath.c_str());
            return ArResolverContext(map_iter->second.ctx);
        }else{
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Reusing context on different stage, reloading due to changed timestamp\n", assetPath.c_str());
            map_iter->second.ctx.LoadOrRefreshData();
            return ArResolverContext(map_iter->second.ctx);
        }
    }
    // Create new context
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_CreateDefaultContextForAsset('%s') - Constructing new context\n", assetPath.c_str());
    std::string assetDir = TfGetPathName(TfAbsPath(resolvedPathStr));
    struct PythonResolverContextRecord record;
    record.timestamp = this->_GetModificationTimestamp(assetPath, resolvedPath);
    record.ctx = PythonResolverContext(resolvedPath);;
    _sharedContexts.insert(std::pair<std::string, PythonResolverContextRecord>(resolvedPath, record));
    return ArResolverContext(record.ctx);
}

bool
PythonResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_IsContextDependentPath()\n");
    bool pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._IsContextDependentPath",
                                     &pythonResult, assetPath);
    if (!state) {
        std::cerr << "Failed to call Resolver._IsContextDependentPath in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

void
PythonResolver::_RefreshContext(
    const ArResolverContext& context)
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("Resolver::_RefreshContext()\n");
    const PythonResolverContext* ctx = this->_GetCurrentContextPtr();
    if (!ctx) {
        return;
    }
    ArNotice::ResolverChanged(*ctx).Send();
}

ArTimestamp
PythonResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "Resolver::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    ArTimestamp pythonResult;
    int state = TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                                     "Resolver._GetModificationTimestamp",
                                     &pythonResult, assetPath, resolvedPath);
    if (!state) {
        std::cerr << "Failed to call Resolver._GetModificationTimestamp in " << DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME) << ".py. ";
        std::cerr << "Please verify that the python code is valid!" << std::endl;
    }
    return pythonResult;
}

std::shared_ptr<ArAsset>
PythonResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "Resolver::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
PythonResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "Resolver::_OpenAssetForWrite('%s', %d)\n",
        resolvedPath.GetPathString().c_str(),
        static_cast<int>(writeMode));
    return ArFilesystemWritableAsset::Create(resolvedPath, writeMode);
}

const PythonResolverContext* 
PythonResolver::_GetCurrentContextPtr() const
{
    return _GetCurrentContextObject<PythonResolverContext>();
}

PXR_NAMESPACE_CLOSE_SCOPE