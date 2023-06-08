#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)

#include "pxr/pxr.h"
#include "pxr/usd/ar/defaultResolver.h"

#include "resolver.h"

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

void
wrapDefaultResolver()
{
    using This = UsdResolverExampleResolver;

    class_<This, bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
        ("UsdResolverExampleResolver", no_init)
        .def("SetDefaultSearchPath", &This::SetDefaultSearchPath,
             args("searchPath"))
        .staticmethod("SetDefaultSearchPath")
        ;
}