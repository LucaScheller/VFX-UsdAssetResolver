#include <string>

#include "pxr/pxr.h"
#include "pxr/base/tf/pyUtils.h"
#include "pxr/usd/ar/pyResolverContext.h"

#include "../utils/boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)

#include "resolverContext.h"

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
        //.def(init<const std::string&>(args("mappingFile")))
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetMappingFilePath", &This::GetMappingFilePath, return_value_policy<return_by_value>())
        .def("GetMappingPairs", &This::GetMappingPairs, return_value_policy<return_by_value>())
        .def("GetSearchPaths", &This::GetSearchPaths, return_value_policy<return_by_value>())
        .def("GetEnvSearchPaths", &This::GetEnvSearchPaths, return_value_policy<return_by_value>())
        .def("GetCustomSearchPaths", &This::GetCustomSearchPaths, return_value_policy<return_by_value>())
    ;
    ArWrapResolverContextForPython<This>();
}
