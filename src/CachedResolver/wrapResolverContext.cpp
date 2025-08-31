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
_Hash(const CachedResolverContext& ctx)
{
    return hash_value(ctx);
}

static
std::string
_Repr(const CachedResolverContext& ctx)
{
    return TF_PY_REPR_PREFIX + "ResolverContext" +
        (ctx.GetMappingFilePath().empty() ? "()" : 
            "('" + ctx.GetMappingFilePath() + "')");
}

void
wrapResolverContext()
{
    using This = CachedResolverContext;

    python::class_<This>("ResolverContext", python::no_init)
        .def(python::init<>())
        .def(python::init<const std::string&>(python::args("mappingFile")))
        .def(python::self == python::self)
        .def(python::self != python::self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("ClearAndReinitialize", &This::ClearAndReinitialize, "Clear mapping and cache pairs and re-initialize context (with mapping file path)")
        .def("GetMappingFilePath", &This::GetMappingFilePath, python::return_value_policy<python::return_by_value>(), "Get the mapping file path (Defaults to file that the context created via Resolver.CreateDefaultContextForAsset() opened")
        .def("SetMappingFilePath", &This::SetMappingFilePath, "Set the mapping file path")
        .def("RefreshFromMappingFilePath", &This::RefreshFromMappingFilePath, "Reload mapping pairs from the mapping file path")
        .def("GetMappingPairs", &This::GetMappingPairs, python::return_value_policy<python::return_by_value>(), "Returns all mapping pairs as a dict")
        .def("AddMappingPair", &This::AddMappingPair, "Add a mapping pair")
        .def("RemoveMappingByKey", &This::RemoveMappingByKey, "Remove a mapping pair by key")
        .def("RemoveMappingByValue", &This::RemoveMappingByValue, "Remove a mapping pair by value")
        .def("ClearMappingPairs", &This::ClearMappingPairs, "Clear all mapping pairs")
        .def("GetCachingPairs", &This::GetCachingPairs, python::return_value_policy<python::return_by_value>(), "Returns all caching pairs as a dict")
        .def("AddCachingPair", &This::AddCachingPair, "Add a caching pair")
        .def("RemoveCachingByKey", &This::RemoveCachingByKey, "Remove a caching pair by key")
        .def("RemoveCachingByValue", &This::RemoveCachingByValue, "Remove a caching pair by value")
        .def("ClearCachingPairs", &This::ClearCachingPairs, "Clear all caching pairs")
    ;
    ArWrapResolverContextForPython<This>();
}
