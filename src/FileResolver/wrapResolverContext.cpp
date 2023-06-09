
#include <string>

#include "boost_include_wrapper.h"

#include "pxr/pxr.h"

#include "resolverContext.h"

#include "pxr/usd/ar/pyResolverContext.h"
#include "pxr/base/tf/pyUtils.h"

#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)


PXR_NAMESPACE_USING_DIRECTIVE

using namespace AR_BOOST_NAMESPACE::python;

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
        (ctx.GetMappingFile().empty() ? "()" : 
            "('" + ctx.GetMappingFile() + "')");
}

void
wrapResolverContext()
{
    using This = FileResolverContext;

    class_<FileResolverContext>("ResolverContext")
        .def(init<const std::string&>(args("mappingFile")))
        
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)

        .def("GetMappingFile", &This::GetMappingFile,
            return_value_policy<return_by_value>())
        ;

    ArWrapResolverContextForPython<This>();
}
