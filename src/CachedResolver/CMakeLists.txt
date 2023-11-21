### CPP Settings ###
# Preprocessor Defines (Same as #define)
# This is a hacky way of preprocessing the class name to a custom name.
# It is not advised to do this in a production setup! (https://stackoverflow.com/questions/20979584)
# add_compile_definitions(CachedResolver=${AR_CACHEDRESOLVER_USD_CXX_CLASS_NAME})
if (WIN32)
    add_compile_definitions(AR_CACHEDRESOLVER_EXPORTS)
endif()

### Targets ###
## Target library > cachedResolver ##
add_library(${AR_CACHEDRESOLVER_TARGET_LIB}
    SHARED
        debugCodes.cpp
        resolver.cpp
        resolverContext.cpp
        resolverTokens.cpp
        # Since when our resolver calls into Python it passes the ResolverContext,
        # we need to ensure that Python has loaded the ResolverContext C++ representation.
        # While we do have duplicate compiled code by adding the below, this allows us to not do hacky workarounds like
        # LD_PRELOAD-ing the lib. See https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/3 for more information.
        # If you know a better way around this please file a PR :)
        module.cpp
        moduleDeps.cpp
        wrapResolver.cpp
        wrapResolverContext.cpp
        wrapResolverTokens.cpp
)
set_boost_namespace(${AR_CACHEDRESOLVER_TARGET_LIB})
# Libs
target_link_libraries(${AR_CACHEDRESOLVER_TARGET_LIB}
    ${AR_PXR_LIB_PREFIX}arch
    ${AR_PXR_LIB_PREFIX}tf
    ${AR_PXR_LIB_PREFIX}gf
    ${AR_PXR_LIB_PREFIX}vt
    ${AR_PXR_LIB_PREFIX}ar
    ${AR_PXR_LIB_PREFIX}sdf
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_CACHEDRESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_CACHEDRESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_CACHEDRESOLVER_TARGET_LIB}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}
        AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME=${AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}
        AR_CACHEDRESOLVER_USD_PLUGIN_NAME=${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}
        AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME=${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME}
        AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME=${AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}

)
# Install
configure_file(plugInfo.json.in plugInfo.json)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json DESTINATION ${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/resources)
install(TARGETS ${AR_CACHEDRESOLVER_TARGET_LIB} DESTINATION ${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib)

## Target library > cachedResolver Python ##
add_library(${AR_CACHEDRESOLVER_TARGET_PYTHON}
    SHARED
        module.cpp
        moduleDeps.cpp
        #resolver.cpp
        #resolverTokens.cpp
        #resolverContext.cpp
        wrapResolver.cpp
        wrapResolverContext.cpp
        wrapResolverTokens.cpp
)
add_dependencies(${AR_CACHEDRESOLVER_TARGET_PYTHON} ${AR_CACHEDRESOLVER_TARGET_LIB})
set_boost_namespace(${AR_CACHEDRESOLVER_TARGET_PYTHON})
# Libs
target_link_libraries(${AR_CACHEDRESOLVER_TARGET_PYTHON}
    ${AR_CACHEDRESOLVER_TARGET_LIB}
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_CACHEDRESOLVER_TARGET_PYTHON}
    PUBLIC
        ${AR_BOOST_INCLUDE_DIR}
        ${AR_PYTHON_INCLUDE_DIR}
        ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_CACHEDRESOLVER_TARGET_PYTHON} PROPERTIES PREFIX "")
if (WIN32)
    set_target_properties(${AR_CACHEDRESOLVER_TARGET_PYTHON} PROPERTIES SUFFIX ".pyd")
endif()
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_CACHEDRESOLVER_TARGET_PYTHON}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}
        MFB_PACKAGE_MODULE=${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_NAME}
        AR_CACHEDRESOLVER_USD_PLUGIN_NAME=${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}
        AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME=${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME}
        AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME=${AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}
)
# Install
install (
    FILES __init__.py
    DESTINATION ${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_NAME}
)
install (
    FILES ${AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}.py
    DESTINATION ${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib/python
)
install(
    TARGETS ${AR_CACHEDRESOLVER_TARGET_PYTHON}
    DESTINATION ${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_NAME}
)

# ### Tests ###
set(TESTS_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/testenv)
set(TESTS_ENV_PYTHONPATH "PYTHONPATH=${CMAKE_INSTALL_PREFIX}/${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib/python")
set(TESTS_ENV_PXR_PLUGINPATH_NAME "PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/resources")
set(TESTS_ENV_LD_LIBRARY_PATH "LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/${AR_CACHEDRESOLVER_USD_PLUGIN_NAME}/lib")
set(TESTS_PYTHON_COMMAND $ENV{HFS}/python/bin/python -B -m unittest discover ${TESTS_SOURCE_DIR})

add_test(
    NAME testCachedResolver
    COMMAND ${CMAKE_COMMAND} -E env ${TESTS_ENV_LD_LIBRARY_PATH} ${TESTS_ENV_PYTHONPATH} ${TESTS_ENV_PXR_PLUGINPATH_NAME} ${TESTS_PYTHON_COMMAND}
)