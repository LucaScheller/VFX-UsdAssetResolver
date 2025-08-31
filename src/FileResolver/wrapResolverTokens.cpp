#include "resolverTokens.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

#include <string>

PXR_NAMESPACE_USING_DIRECTIVE

namespace python = AR_BOOST_NAMESPACE::python;

static std::string GetMappingPairs() {
    return FileResolverTokens->mappingPairs.GetString();
}

void wrapResolverTokens()
{
    using This = FileResolverTokensType;

    #if AR_BOOST_PXR_EXTERNAL_EXISTS == 1
        python::class_<This, python::noncopyable>("Tokens", python::no_init)
    #else
        python::class_<This, AR_BOOST_NAMESPACE::noncopyable>("Tokens", python::no_init)
    #endif
        .add_static_property("mappingPairs", python::make_function(&GetMappingPairs, python::return_value_policy<python::return_by_value>()));
}