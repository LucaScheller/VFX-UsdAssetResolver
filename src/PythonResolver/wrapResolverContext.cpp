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
        .def(self == self)
        .def(self != self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetMappingFilePath", &This::GetMappingFilePath, return_value_policy<return_by_value>())
        .def("SetMappingFilePath", &This::SetMappingFilePath)
        .def("GetData", &This::GetData, return_value_policy<return_by_value>())
        .def("SetData", &This::SetData)
        .def("LoadOrRefreshData", &This::LoadOrRefreshData)
    ;
    ArWrapResolverContextForPython<This>();
}
