
#include "pxr/pxr.h"
#include "resolver.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)


using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE


void
wrapResolver()
{
    using This = FileResolver;

    class_<This, bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
        ("FileResolver", no_init)
        .def("SetDefaultSearchPath", &This::SetDefaultSearchPath, args("searchPath"))
        .staticmethod("SetDefaultSearchPath")
        ;
}