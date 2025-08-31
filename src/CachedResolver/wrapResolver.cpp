#include "resolver.h"

#include <pxr/pxr.h>
#include <pxr/usd/ar/resolver.h>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

PXR_NAMESPACE_USING_DIRECTIVE

namespace python = AR_BOOST_NAMESPACE::python;

void
wrapResolver()
{
    using This = CachedResolver;

    #if AR_BOOST_PXR_EXTERNAL_EXISTS == 1
        python::class_<This, python::bases<ArResolver>, python::noncopyable>
    #else
        python::class_<This, python::bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
    #endif
        ("Resolver", python::no_init)
        .def("GetExposeAbsolutePathIdentifierState", &This::GetExposeAbsolutePathIdentifierState, python::return_value_policy<python::return_by_value>(), "Get the state of exposing absolute path identifiers")
        .def("SetExposeAbsolutePathIdentifierState", &This::SetExposeAbsolutePathIdentifierState, "Set the state of exposing absolute path identifiers")
        .def("GetExposeRelativePathIdentifierState", &This::GetExposeRelativePathIdentifierState, python::return_value_policy<python::return_by_value>(), "Get the state of exposing relative path identifiers")
        .def("SetExposeRelativePathIdentifierState", &This::SetExposeRelativePathIdentifierState, "Set the state of exposing relative path identifiers")
        .def("GetCachedRelativePathIdentifierPairs", &This::GetCachedRelativePathIdentifierPairs, python::return_value_policy<python::return_by_value>(), "Returns all cached relative path identifier pairs as a dict")
        .def("AddCachedRelativePathIdentifierPair", &This::AddCachedRelativePathIdentifierPair, "Add a cached relative path identifier pair")
        .def("RemoveCachedRelativePathIdentifierByKey", &This::RemoveCachedRelativePathIdentifierByKey, "Remove a cached relative path identifier pair by key")
        .def("RemoveCachedRelativePathIdentifierByValue", &This::RemoveCachedRelativePathIdentifierByValue, "Remove a cached relative path identifier pair by value")
        .def("ClearCachedRelativePathIdentifierPairs", &This::ClearCachedRelativePathIdentifierPairs, "Clear all cached relative path identifier pairs")
    ;
}
