#include "resolver.h"

#include <pxr/pxr.h>

#include "pxr/external/boost/python.hpp"

PXR_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

void
wrapResolver()
{
    using This = CachedResolver;

    class_<This, bases<ArResolver>, noncopyable>
        ("Resolver", no_init)
    ;
}
