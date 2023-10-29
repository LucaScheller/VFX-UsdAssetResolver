
#include "resolver.h"

#include <pxr/pxr.h>

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python/class.hpp)
#include BOOST_INCLUDE(python/return_value_policy.hpp)

using namespace AR_BOOST_NAMESPACE::python;

PXR_NAMESPACE_USING_DIRECTIVE

void
wrapResolver()
{
    using This = FileResolver;

    class_<This, bases<ArResolver>, AR_BOOST_NAMESPACE::noncopyable>
        ("Resolver", no_init)
    ;
}