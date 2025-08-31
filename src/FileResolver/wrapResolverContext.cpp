#include "resolverContext.h"

#include "pxr/pxr.h"
#include "pxr/base/tf/pyUtils.h"
#include "pxr/usd/ar/pyResolverContext.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include <string>

PXR_NAMESPACE_USING_DIRECTIVE

namespace python = AR_BOOST_NAMESPACE::python;

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
    
    python::class_<FileResolverContext>("ResolverContext", python::no_init)
        .def(python::init<>())
        .def(python::init<const std::string&>(python::args("mappingFile")))
        .def(python::init<const std::vector<std::string>&>(python::args("searchPaths")))
        .def(python::init<const std::string&, const std::vector<std::string>&>(python::args("mappingFile", "searchPaths")))
        .def(python::self == python::self)
        .def(python::self != python::self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetSearchPaths", &This::GetSearchPaths, python::return_value_policy<python::return_by_value>(), "Return all search paths (env and custom)")
        .def("RefreshSearchPaths", &This::RefreshSearchPaths, "Reload env search paths and re-populates the search paths that the resolver uses. This must be called after changing the env var value or the custom search paths.")
        .def("GetEnvSearchPaths", &This::GetEnvSearchPaths, python::return_value_policy<python::return_by_value>(), "Return all env search paths")
        .def("GetCustomSearchPaths", &This::GetCustomSearchPaths, python::return_value_policy<python::return_by_value>(), "Return all custom search paths")
        .def("SetCustomSearchPaths", &This::SetCustomSearchPaths, "Set custom search paths")
        .def("GetMappingFilePath", &This::GetMappingFilePath, python::return_value_policy<python::return_by_value>(), "Get the mapping file path (Defaults file that the context created Resolver.CreateDefaultContextForAsset() opened)")
        .def("SetMappingFilePath", &This::SetMappingFilePath, "Set the mapping file path")
        .def("RefreshFromMappingFilePath", &This::RefreshFromMappingFilePath, "Reload mapping pairs from the mapping file path")
        .def("GetMappingPairs", &This::GetMappingPairs, python::return_value_policy<python::return_by_value>(), "Returns all mapping pairs as a dict")
        .def("AddMappingPair", &This::AddMappingPair, "Add a mapping pair")
        .def("RemoveMappingByKey", &This::RemoveMappingByKey, "Remove a mapping pair by key")
        .def("RemoveMappingByValue", &This::RemoveMappingByValue, "Remove a mapping pair by value")
        .def("ClearMappingPairs", &This::ClearMappingPairs, "Clear all mapping pairs")
        .def("GetMappingRegexExpression", &This::GetMappingRegexExpressionStr, python::return_value_policy<python::return_by_value>(), "Get the regex expression")
        .def("SetMappingRegexExpression", &This::SetMappingRegexExpression, "Set the regex expression")
        .def("GetMappingRegexFormat", &This::GetMappingRegexFormat, python::return_value_policy<python::return_by_value>(), "Get the regex expression substitution formatting")
        .def("SetMappingRegexFormat", &This::SetMappingRegexFormat, "Set the regex expression substitution formatting")
    ;
    ArWrapResolverContextForPython<This>();
}
