#ifndef AR_FILERESOLVER_RESOLVER_CONTEXT_H
#define AR_FILERESOLVER_RESOLVER_CONTEXT_H

#include <string>

#include "pxr/pxr.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include "api.h"


class FileResolverContext
{
public:
    // Constructors
    FileResolverContext();
    AR_FILERESOLVER_API
    FileResolverContext(const FileResolverContext& ctx);
    AR_FILERESOLVER_API
    FileResolverContext(const std::string& mappingFilePath);
    AR_FILERESOLVER_API
    FileResolverContext(const std::vector<std::string>& searchPaths);
    
    // Standard Ops
    AR_FILERESOLVER_API
    bool operator<(const FileResolverContext& ctx) const;
    AR_FILERESOLVER_API
    bool operator==(const FileResolverContext& ctx) const;
    AR_FILERESOLVER_API
    bool operator!=(const FileResolverContext& ctx) const;
    AR_FILERESOLVER_API
    friend size_t hash_value(const FileResolverContext& ctx);

    // Methods
    AR_FILERESOLVER_API
    const std::string& GetMappingFilePath();
    AR_FILERESOLVER_API
    void SetMappingFilePath(std::string);

    AR_FILERESOLVER_API
    std::vector<std::string> GetSearchPaths();
    AR_FILERESOLVER_API
    void RefreshSearchPaths();
    AR_FILERESOLVER_API
    std::vector<std::string> GetEnvSearchPaths();
    AR_FILERESOLVER_API
    std::vector<std::string> GetCustomSearchPaths();
    AR_FILERESOLVER_API
    void SetCustomSearchPaths(const std::vector<std::string>& searchPaths);

private:
    // Vars
    std::string _mappingFilePath;
    std::map<std::string, std::string> _mappingPairs;
    std::vector<std::string> _searchPaths;
    std::vector<std::string> _envSearchPaths;
    std::vector<std::string> _customSearchPaths;
    // Methods
    void _LoadEnvSearchPaths();
};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(FileResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_CONTEXT_H