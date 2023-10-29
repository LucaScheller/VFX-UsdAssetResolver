#include "resolverContext.h"

#include "pxr/pxr.h"
#include "pxr/base/tf/pyUtils.h"
#include "pxr/usd/ar/pyResolverContext.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/operators.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)

#include <string>

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

static
size_t
_Hash(const FileResolverContext& ctx)
{
    return hash_value(ctx);
}

static
std::string
_Repr(const FileResolverContext& ctx)
{
    return TF_PY_REPR_PREFIX + "ResolverContext" +
        (ctx.GetMappingFilePath().empty() ? "()" : 
            "('" + ctx.GetMappingFilePath() + "')");
}

void
wrapResolverContext()
{
    using This = FileResolverContext;

    class_<FileResolverContext>("ResolverContext", no_init)
        .def(init<>())
        .def(init<const std::string&>(args("mappingFile")))
        .def(init<const std::vector<std::string>&>(args("searchPaths")))
        .def(init<const std::string&, const std::vector<std::string>&>(args("mappingFile", "searchPaths")))
        .def(self == self)
        .def(self != self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetSearchPaths", &This::GetSearchPaths, return_value_policy<return_by_value>(), "Return all search paths (env and custom)")
        .def("RefreshSearchPaths", &This::RefreshSearchPaths, "Reload env search paths and re-populates the search paths that the resolver uses. This must be called after changing the env var value or the custom search paths.")
        .def("GetEnvSearchPaths", &This::GetEnvSearchPaths, return_value_policy<return_by_value>(), "Return all env search paths")
        .def("GetCustomSearchPaths", &This::GetCustomSearchPaths, return_value_policy<return_by_value>(), "Return all custom search paths")
        .def("SetCustomSearchPaths", &This::SetCustomSearchPaths, "Set custom search paths")
        .def("GetMappingFilePath", &This::GetMappingFilePath, return_value_policy<return_by_value>(), "Get the mapping file path (Defaults file that the context created Resolver.CreateDefaultContextForAsset() opened)")
        .def("SetMappingFilePath", &This::SetMappingFilePath, "Set the mapping file path")
        .def("RefreshFromMappingFilePath", &This::RefreshFromMappingFilePath, "Reload mapping pairs from the mapping file path")
        .def("GetMappingPairs", &This::GetMappingPairs, return_value_policy<return_by_value>(), "Returns all mapping pairs as a dict")
        .def("AddMappingPair", &This::AddMappingPair, "Add a mapping pair")
        .def("RemoveMappingByKey", &This::RemoveMappingByKey, "Remove a mapping pair by key")
        .def("RemoveMappingByValue", &This::RemoveMappingByValue, "Remove a mapping pair by value")
        .def("ClearMappingPairs", &This::ClearMappingPairs, "Clear all mapping pairs")
        .def("GetMappingRegexExpression", &This::GetMappingRegexExpressionStr, return_value_policy<return_by_value>(), "Get the regex expression")
        .def("SetMappingRegexExpression", &This::SetMappingRegexExpression, "Set the regex expression")
        .def("GetMappingRegexFormat", &This::GetMappingRegexFormat, return_value_policy<return_by_value>(), "Get the regex expression substitution formatting")
        .def("SetMappingRegexFormat", &This::SetMappingRegexFormat, "Set the regex expression substitution formatting")
    ;
    ArWrapResolverContextForPython<This>();
}
