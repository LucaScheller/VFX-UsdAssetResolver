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

        .def("ClearMappingPairs", &This::ClearMappingPairs, "Clear all mapping pairs")
    ;
    ArWrapResolverContextForPython<This>();
}
