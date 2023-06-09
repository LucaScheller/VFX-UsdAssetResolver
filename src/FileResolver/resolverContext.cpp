#include "pxr/pxr.h"

#include "pxr/base/tf/pathUtils.h"

#include "resolverContext.h"

PXR_NAMESPACE_USING_DIRECTIVE

FileResolverContext::FileResolverContext()
    = default;

FileResolverContext::FileResolverContext(
    const FileResolverContext&) = default;

FileResolverContext::FileResolverContext(
    const std::string& mappingFile)
    : _mappingFile(TfAbsPath(mappingFile))
{
}

bool
FileResolverContext::operator<(
    const FileResolverContext& rhs) const
{
    return _mappingFile < rhs._mappingFile;
}

bool
FileResolverContext::operator==(
    const FileResolverContext& rhs) const
{
    return _mappingFile == rhs._mappingFile;
}
    
size_t hash_value(const FileResolverContext& ctx)
{
    return TfHash()(ctx._mappingFile);
}

const std::string& 
FileResolverContext::GetMappingFile() const
{
    return _mappingFile;
}
