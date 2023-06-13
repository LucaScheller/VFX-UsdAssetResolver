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
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("::_CreateIdentifier('%s', '%s')\n",
                                          assetPath.c_str(), anchorAssetPath.GetPathString().c_str());
    std::string pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._CreateIdentifier",
                         &pythonResult, assetPath, anchorAssetPath);
    return pythonResult;
}

std::string
PythonResolver::_CreateIdentifierForNewAsset(
    const std::string& assetPath,
    const ArResolvedPath& anchorAssetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::_CreateIdentifierForNewAsset ('%s', '%s')\n",
        assetPath.c_str(), anchorAssetPath.GetPathString().c_str());
    std::string pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._CreateIdentifierForNewAsset",
                         &pythonResult, assetPath, anchorAssetPath);
    return pythonResult;
}

ArResolvedPath
PythonResolver::_Resolve(
    const std::string& assetPath) const
{
    const FileResolverContext* contexts[2] = {this->_GetCurrentContextPtr(), &_fallbackContext};
    const std::string &serializedContext = ;
    const std::string &serializedFallbackContext = ; 
    ArResolvedPath pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._Resolve",
                         &pythonResult, assetPath, this->_GetCurrentContextPtr());
    return pythonResult;
}

ArResolvedPath
PythonResolver::_ResolveForNewAsset(
    const std::string& assetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg("::_ResolveForNewAsset('%s')\n", assetPath.c_str());
    ArResolvedPath pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._ResolveForNewAsset",
                         &pythonResult, assetPath);
    return pythonResult;
}

ArResolverContext
PythonResolver::_CreateDefaultContext() const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContext()\n");
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
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s')\n", assetPath.c_str());
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
        TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Skipping on same stage\n", assetPath.c_str());
        return ArResolverContext(_fallbackContext);
    }
    auto map_iter = _sharedContexts.find(resolvedPath);
    if(map_iter != _sharedContexts.end()){
        if (map_iter->second.timestamp.GetTime() == this->_GetModificationTimestamp(assetPath, resolvedPath).GetTime())
        {
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Reusing context on different stage\n", assetPath.c_str());
            return ArResolverContext(map_iter->second.ctx);
        }else{
            TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Reusing context on different stage, reloading due to changed timestamp\n", assetPath.c_str());
            map_iter->second.ctx.RefreshFromMappingFilePath();
            return ArResolverContext(map_iter->second.ctx);
        }
    }
    // Create new context
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_CreateDefaultContextForAsset('%s') - Constructing new context\n", assetPath.c_str());
    std::string assetDir = TfGetPathName(TfAbsPath(resolvedPathStr));
    struct PythonResolverContextRecord record;
    record.timestamp = this->_GetModificationTimestamp(assetPath, resolvedPath);
    record.ctx = PythonResolverContext(resolvedPath, std::vector<std::string>(1, assetDir));;
    _sharedContexts.insert(std::pair<std::string, PythonResolverContextRecord>(resolvedPath, record));
    return ArResolverContext(record.ctx);
}

bool
PythonResolver::_IsContextDependentPath(
    const std::string& assetPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_IsContextDependentPath()\n");
    bool pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._IsContextDependentPath",
                         &pythonResult, assetPath);
    return pythonResult;
}

void
PythonResolver::_RefreshContext(
    const ArResolverContext& context)
{
    const PythonResolverContext* ctx = this->_GetCurrentContextPtr();
    if (!ctx) {
        return;
    }
    TF_DEBUG(PYTHONRESOLVER_RESOLVER_CONTEXT).Msg("::_RefreshContext()\n");
    ArNotice::ResolverChanged(*ctx).Send();
}

ArTimestamp
PythonResolver::_GetModificationTimestamp(
    const std::string& assetPath,
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::GetModificationTimestamp('%s', '%s')\n",
        assetPath.c_str(), resolvedPath.GetPathString().c_str());
    ArTimestamp pythonResult;
    TfPyInvokeAndExtract(DEFINE_STRING(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME),
                         "Resolver._GetModificationTimestamp",
                         &pythonResult, assetPath, resolvedPath);
    return pythonResult;
}

std::shared_ptr<ArAsset>
PythonResolver::_OpenAsset(
    const ArResolvedPath& resolvedPath) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::OpenAsset('%s')\n",
        resolvedPath.GetPathString().c_str());
    return ArFilesystemAsset::Open(resolvedPath);
}

std::shared_ptr<ArWritableAsset>
PythonResolver::_OpenAssetForWrite(
    const ArResolvedPath& resolvedPath,
    WriteMode writeMode) const
{
    TF_DEBUG(PYTHONRESOLVER_RESOLVER).Msg(
        "::_OpenAssetForWrite('%s', %d)\n",
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