#include "resolverTokens.h"

#include "boost_include_wrapper.h"
#include BOOST_INCLUDE(python.hpp)

PXR_NAMESPACE_USING_DIRECTIVE

namespace python = AR_BOOST_NAMESPACE::python;

static std::string GetMappingPairs() {
    return PythonResolverTokens->mappingPairs.GetString();
}

static std::string GetMappingRegexExpression() {
    return PythonResolverTokens->mappingRegexExpression.GetString();
}

static std::string GetMappingRegexFormat() {
    return PythonResolverTokens->mappingRegexFormat.GetString();
}

static std::string GetSearchPaths() {
    return PythonResolverTokens->searchPaths.GetString();
}

void wrapResolverTokens()
{
    using This = PythonResolverTokensType;

    #if AR_BOOST_PXR_EXTERNAL_EXISTS == 1
        python::class_<This, python::noncopyable>("Tokens", python::no_init)
    #else
        python::class_<This, AR_BOOST_NAMESPACE::noncopyable>("Tokens", python::no_init)
    #endif
        .add_static_property("mappingPairs", python::make_function(&GetMappingPairs, python::return_value_policy<python::return_by_value>()))
        .add_static_property("mappingRegexExpression", python::make_function(&GetMappingRegexExpression, python::return_value_policy<python::return_by_value>()))
        .add_static_property("mappingRegexFormat", python::make_function(&GetMappingRegexFormat, python::return_value_policy<python::return_by_value>()))
        .add_static_property("searchPaths", python::make_function(&GetSearchPaths, python::return_value_policy<python::return_by_value>()));
}