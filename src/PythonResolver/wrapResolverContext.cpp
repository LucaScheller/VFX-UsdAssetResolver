#include <string>

#include "pxr/pxr.h"
#include "pxr/base/tf/pyUtils.h"
#include "pxr/usd/ar/pyResolverContext.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/operators.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)

#include "resolverContext.h"

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

static
size_t
_Hash(const PythonResolverContext& ctx)
{
    return hash_value(ctx);
}

static
std::string
_Repr(const PythonResolverContext& ctx)
{
    return TF_PY_REPR_PREFIX + "ResolverContext" +
        (ctx.GetMappingFilePath().empty() ? "()" : 
            "('" + ctx.GetMappingFilePath() + "')");
}

void
wrapResolverContext()
{
    using This = PythonResolverContext;

    class_<PythonResolverContext>("ResolverContext", no_init)
        .def(init<>())
        .def(init<const std::string&>(args("mappingFile")))
        .def(init<const std::vector<std::string>&>(args("searchPaths")))
        .def(init<const std::string&, const std::vector<std::string>&>(args("mappingFile", "searchPaths")))
        .def(self == self)
        .def(self != self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetSearchPaths", &This::GetSearchPaths, return_value_policy<return_by_value>())
        .def("RefreshSearchPaths", &This::RefreshSearchPaths)
        .def("GetEnvSearchPaths", &This::GetEnvSearchPaths, return_value_policy<return_by_value>())
        .def("GetCustomSearchPaths", &This::GetCustomSearchPaths, return_value_policy<return_by_value>())
        .def("SetCustomSearchPaths", &This::SetCustomSearchPaths)
        .def("GetMappingFilePath", &This::GetMappingFilePath, return_value_policy<return_by_value>())
        .def("SetMappingFilePath", &This::SetMappingFilePath)
        .def("RefreshFromMappingFilePath", &This::RefreshFromMappingFilePath)
        .def("GetMappingPairs", &This::GetMappingPairs, return_value_policy<return_by_value>())
        .def("AddMappingPair", &This::AddMappingPair)
        .def("RemoveMappingByKey", &This::RemoveMappingByKey)
        .def("RemoveMappingByValue", &This::RemoveMappingByValue)
        .def("ClearMappingPairs", &This::ClearMappingPairs)
        .def("GetMappingRegexExpression", &This::GetMappingRegexExpressionStr, return_value_policy<return_by_value>())
        .def("SetMappingRegexExpression", &This::SetMappingRegexExpression)
        .def("GetMappingRegexFormat", &This::GetMappingRegexFormat, return_value_policy<return_by_value>())
        .def("SetMappingRegexFormat", &This::SetMappingRegexFormat)
    ;
    ArWrapResolverContextForPython<This>();
}
