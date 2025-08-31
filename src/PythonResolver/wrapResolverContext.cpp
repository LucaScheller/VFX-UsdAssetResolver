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

    python::class_<PythonResolverContext>("ResolverContext", python::no_init)
        .def(python::init<>())
        .def(python::init<const std::string&>(python::args("mappingFile")))
        .def(python::self == python::self)
        .def(python::self != python::self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("GetMappingFilePath", &This::GetMappingFilePath, python::return_value_policy<python::return_by_value>())
        .def("SetMappingFilePath", &This::SetMappingFilePath)
        .def("GetData", &This::GetData, python::return_value_policy<python::return_by_value>())
        .def("SetData", &This::SetData)
        .def("LoadOrRefreshData", &This::LoadOrRefreshData)
    ;
    ArWrapResolverContextForPython<This>();
}
