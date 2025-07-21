#include "resolverTokens.h"

#include "pxr/external/boost/python.hpp"

PXR_NAMESPACE_USING_DIRECTIVE

using namespace pxr_boost::python;

// NOTE: When migrating to pxr_boost::python (usd-24.11+), I had to replace the operator
// based token getter with static function(s) because we don't have access to boost::mpl::vector for
// signature anymore. Anyways we have only one token and setting up new getters is nothing if we need to.
static std::string GetMappingPairs() {
    return CachedResolverTokens->mappingPairs.GetString();
}

void wrapResolverTokens()
{
    class_<CachedResolverTokensType, noncopyable>("Tokens", no_init)
        .add_static_property("mappingPairs",
            make_function(&GetMappingPairs,
                return_value_policy<return_by_value>()));
}
