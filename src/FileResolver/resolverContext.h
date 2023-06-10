#ifndef AR_FILERESOLVER_RESOLVER_CONTEXT_H
#define AR_FILERESOLVER_RESOLVER_CONTEXT_H

#include <memory>
#include <regex>
#include <string>

#include "pxr/pxr.h"
#include "pxr/usd/ar/defineResolverContext.h"
#include "pxr/usd/ar/resolverContext.h"

#include "api.h"
#include "debugCodes.h"


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
    AR_FILERESOLVER_API
    FileResolverContext(const std::string& mappingFilePath, const std::vector<std::string>& searchPaths);
    
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
    std::vector<std::string> GetSearchPaths() const { return _searchPaths; }
    AR_FILERESOLVER_API
    void RefreshSearchPaths();
    AR_FILERESOLVER_API
    std::vector<std::string> GetEnvSearchPaths() const { return _envSearchPaths; }
    AR_FILERESOLVER_API
    std::vector<std::string> GetCustomSearchPaths() const { return _customSearchPaths; }
    AR_FILERESOLVER_API
    void SetCustomSearchPaths(const std::vector<std::string>& searchPaths);

    AR_FILERESOLVER_API
    const std::string& GetMappingFilePath() const { return *_mappingFilePath;}
    AR_FILERESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { *_mappingFilePath = mappingFilePath; }
    AR_FILERESOLVER_API
    void RefreshFromMappingFilePath();
    AR_FILERESOLVER_API
    void AddMappingPair(const std::string& sourceStr, const std::string& targetStr);
    AR_FILERESOLVER_API
    void RemoveMappingByKey(const std::string& sourceStr);
    AR_FILERESOLVER_API
    void RemoveMappingByValue(const std::string& targetStr);
    AR_FILERESOLVER_API
    const std::map<std::string, std::string>& GetMappingPairs() const { return _mappingPairs; }
    AR_FILERESOLVER_API
    void ClearMappingPairs() { _mappingPairs.clear(); }
    AR_FILERESOLVER_API
    const std::regex& GetMappingRegexExpression() const { return _mappingRegexExpression; }
    AR_FILERESOLVER_API
    const std::string& GetMappingRegexExpressionStr() const { return _mappingRegexExpressionStr; }
    AR_FILERESOLVER_API
    void SetMappingRegexExpression(std::string& mappingRegexExpressionStr) { 
        _mappingRegexExpressionStr = mappingRegexExpressionStr;
        _mappingRegexExpression = std::regex(mappingRegexExpressionStr);
    }
    AR_FILERESOLVER_API
    const std::string& GetMappingRegexFormat() const { return _mappingRegexFormat; }
    AR_FILERESOLVER_API
    void SetMappingRegexFormat(std::string& mappingRegexFormat) { _mappingRegexFormat = mappingRegexFormat; }

private:
    // Vars
    std::vector<std::string> _searchPaths;
    std::vector<std::string> _envSearchPaths;
    std::vector<std::string> _customSearchPaths;
    std::shared_ptr<std::string> _mappingFilePath{ new std::string}; 
    std::map<std::string, std::string> _mappingPairs;
    std::regex _mappingRegexExpression;
    std::string _mappingRegexExpressionStr;
    std::string _mappingRegexFormat;
    
    // Methods
    void _LoadEnvMappingRegex();
    void _LoadEnvSearchPaths();
    bool _GetMappingPairsFromUsdFile(const std::string& filePath);

};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(FileResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_CONTEXT_H