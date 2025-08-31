#include "resolver.h"

#include <pxr/pxr.h>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

PXR_NAMESPACE_USING_DIRECTIVE

namespace python = AR_BOOST_NAMESPACE::python;

void
wrapResolver()
{
    using This = PythonResolver;

    #if AR_BOOST_PXR_EXTERNAL_EXISTS == 1
        python::class_<This, python::bases<ArResolver>, python::noncopyable>
    #else
        python::class_<This, python::bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
    #endif
        ("Resolver", python::no_init);
}