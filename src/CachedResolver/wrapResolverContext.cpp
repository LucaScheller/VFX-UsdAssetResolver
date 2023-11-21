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

    class_<This>("ResolverContext", no_init)
        .def(init<>())
        .def(init<const std::string&>(args("mappingFile")))
        .def(self == self)
        .def(self != self)
        .def("__hash__", _Hash)
        .def("__repr__", _Repr)
        .def("ClearAndReinitialize", &This::ClearAndReinitialize, "Clear mapping and cache pairs and re-initialize context (with mapping file path)")
        .def("GetMappingFilePath", &This::GetMappingFilePath, return_value_policy<return_by_value>(), "Get the mapping file path (Defaults to file that the context created via Resolver.CreateDefaultContextForAsset() opened")
        .def("SetMappingFilePath", &This::SetMappingFilePath, "Set the mapping file path")
        .def("RefreshFromMappingFilePath", &This::RefreshFromMappingFilePath, "Reload mapping pairs from the mapping file path")
        .def("GetMappingPairs", &This::GetMappingPairs, return_value_policy<return_by_value>(), "Returns all mapping pairs as a dict")
        .def("AddMappingPair", &This::AddMappingPair, "Add a mapping pair")
        .def("RemoveMappingByKey", &This::RemoveMappingByKey, "Remove a mapping pair by key")
        .def("RemoveMappingByValue", &This::RemoveMappingByValue, "Remove a mapping pair by value")
        .def("ClearMappingPairs", &This::ClearMappingPairs, "Clear all mapping pairs")
        .def("GetCachingPairs", &This::GetCachingPairs, return_value_policy<return_by_value>(), "Returns all caching pairs as a dict")
        .def("AddCachingPair", &This::AddCachingPair, "Add a caching pair")
        .def("RemoveCachingByKey", &This::RemoveCachingByKey, "Remove a caching pair by key")
        .def("RemoveCachingByValue", &This::RemoveCachingByValue, "Remove a caching pair by value")
        .def("ClearCachingPairs", &This::ClearCachingPairs, "Clear all caching pairs")
    ;
    ArWrapResolverContextForPython<This>();
}
