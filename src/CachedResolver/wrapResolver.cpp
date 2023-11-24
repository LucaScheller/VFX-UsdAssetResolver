#include "resolver.h"

#include <pxr/pxr.h>
#include <pxr/usd/ar/resolver.h>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

void
wrapResolver()
{
    using This = CachedResolver;

    class_<This, bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
        ("Resolver", no_init)
        .def("GetExposeRelativePathIdentifierState", &This::GetExposeRelativePathIdentifierState, return_value_policy<return_by_value>(), "Get the state of exposing relative path identifiers")
        .def("SetExposeRelativePathIdentifierState", &This::SetExposeRelativePathIdentifierState, "Set the state of exposing relative path identifiers")
        .def("GetCachedRelativePathIdentifierPairs", &This::GetCachedRelativePathIdentifierPairs, return_value_policy<return_by_value>(), "Returns all cached relative path identifier pairs as a dict")
        .def("AddCachedRelativePathIdentifierPair", &This::AddCachedRelativePathIdentifierPair, "Add a cached relative path identifier pair")
        .def("RemoveCachedRelativePathIdentifierByKey", &This::RemoveCachedRelativePathIdentifierByKey, "Remove a cached relative path identifier pair by key")
        .def("RemoveCachedRelativePathIdentifierByValue", &This::RemoveCachedRelativePathIdentifierByValue, "Remove a cached relative path identifier pair by value")
        .def("ClearCachedRelativePathIdentifierPairs", &This::ClearCachedRelativePathIdentifierPairs, "Clear all cached relative path identifier pairs")
    ;
}