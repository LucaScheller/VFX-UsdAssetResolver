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

/* Data Model
We use an internal data struct that is accessed via a shared pointer
as Usd currently creates resolver context copies when exposed via python
instead of passing thru the pointer. This way we can send
> ArNotice::ResolverChanged(*ctx).Send();
notifications to the stages.
> See for more info: https://groups.google.com/g/usd-interest/c/9JrXGGbzBnQ/m/_f3oaqBdAwAJ
*/
struct FileResolverContextInternalData
{
    std::vector<std::string> searchPaths;
    std::vector<std::string> envSearchPaths;
    std::vector<std::string> customSearchPaths;
    std::string mappingFilePath;
    std::map<std::string, std::string> mappingPairs;
    std::regex mappingRegexExpression;
    std::string mappingRegexExpressionStr;
    std::string mappingRegexFormat;
};

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
    std::vector<std::string> GetSearchPaths() const { return data->searchPaths; }
    AR_FILERESOLVER_API
    void RefreshSearchPaths();
    AR_FILERESOLVER_API
    std::vector<std::string> GetEnvSearchPaths() const { return data->envSearchPaths; }
    AR_FILERESOLVER_API
    std::vector<std::string> GetCustomSearchPaths() const { return data->customSearchPaths; }
    AR_FILERESOLVER_API
    void SetCustomSearchPaths(const std::vector<std::string>& searchPaths);

    AR_FILERESOLVER_API
    const std::string& GetMappingFilePath() const { return data->mappingFilePath;}
    AR_FILERESOLVER_API
    void SetMappingFilePath(std::string mappingFilePath) { data->mappingFilePath = mappingFilePath; }
    AR_FILERESOLVER_API
    void RefreshFromMappingFilePath();
    AR_FILERESOLVER_API
    void AddMappingPair(const std::string& sourceStr, const std::string& targetStr);
    AR_FILERESOLVER_API
    void RemoveMappingByKey(const std::string& sourceStr);
    AR_FILERESOLVER_API
    void RemoveMappingByValue(const std::string& targetStr);
    AR_FILERESOLVER_API
    const std::map<std::string, std::string>& GetMappingPairs() const { return data->mappingPairs; }
    AR_FILERESOLVER_API
    void ClearMappingPairs() { data->mappingPairs.clear(); }
    AR_FILERESOLVER_API
    const std::regex& GetMappingRegexExpression() const { return data->mappingRegexExpression; }
    AR_FILERESOLVER_API
    const std::string& GetMappingRegexExpressionStr() const { return data->mappingRegexExpressionStr; }
    AR_FILERESOLVER_API
    void SetMappingRegexExpression(std::string& mappingRegexExpressionStr) { 
        data->mappingRegexExpressionStr = mappingRegexExpressionStr;
        data->mappingRegexExpression = std::regex(mappingRegexExpressionStr);
    }
    AR_FILERESOLVER_API
    const std::string& GetMappingRegexFormat() const { return data->mappingRegexFormat; }
    AR_FILERESOLVER_API
    void SetMappingRegexFormat(std::string& mappingRegexFormat) { data->mappingRegexFormat = mappingRegexFormat; }

private:
    // Vars
    std::shared_ptr<FileResolverContextInternalData> data = std::make_shared<FileResolverContextInternalData>();
    
    // Methods
    void _LoadEnvMappingRegex();
    void _LoadEnvSearchPaths();
    bool _GetMappingPairsFromUsdFile(const std::string& filePath);

};

PXR_NAMESPACE_OPEN_SCOPE
AR_DECLARE_RESOLVER_CONTEXT(FileResolverContext);
PXR_NAMESPACE_CLOSE_SCOPE

#endif // AR_FILERESOLVER_RESOLVER_CONTEXT_H