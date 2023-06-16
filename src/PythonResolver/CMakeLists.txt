### CPP Settings ###
SET(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/dist/${AR_PYTHONRESOLVER_USD_PLUGIN_NAME}" CACHE PATH "Default install dir " FORCE)

# Preprocessor Defines (Same as #define)
# This is a hacky way of preprocessing the class name to a custom name.
# It is not advised to do this in a production setup! (https://stackoverflow.com/questions/20979584)
# add_compile_definitions(PythonResolver=${AR_PYTHONRESOLVER_USD_CXX_CLASS_NAME})

### Targets ###
## Target library > PYTHONRESOLVER ##
add_library(${AR_PYTHONRESOLVER_TARGET_LIB}
    SHARED
        debugCodes.cpp
        resolver.cpp
        resolverContext.cpp
        resolverTokens.cpp
)
set_boost_namespace(${AR_PYTHONRESOLVER_TARGET_LIB})
# Libs
target_link_libraries(${AR_PYTHONRESOLVER_TARGET_LIB}
    ${AR_PXR_LIB_PREFIX}arch
    ${AR_PXR_LIB_PREFIX}tf
    ${AR_PXR_LIB_PREFIX}gf
    ${AR_PXR_LIB_PREFIX}js
    ${AR_PXR_LIB_PREFIX}vt
    ${AR_PXR_LIB_PREFIX}ar
)
# Headers
target_include_directories(${AR_PYTHONRESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_PYTHONRESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_PYTHONRESOLVER_TARGET_LIB}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_PYTHONRESOLVER_USD_PLUGIN_NAME}
        AR_ENV_SEARCH_PATHS=${AR_ENV_SEARCH_PATHS}
        AR_ENV_SEARCH_REGEX_EXPRESSION=${AR_ENV_SEARCH_REGEX_EXPRESSION}
        AR_ENV_SEARCH_REGEX_FORMAT=${AR_ENV_SEARCH_REGEX_FORMAT}
        AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME=${AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}
)
# Install
configure_file(plugInfo.json.in plugInfo.json)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json DESTINATION resources)
install(TARGETS ${AR_PYTHONRESOLVER_TARGET_LIB} RUNTIME DESTINATION lib)

## Target library > PYTHONRESOLVER Python ##
add_library(${AR_PYTHONRESOLVER_TARGET_PYTHON}
    SHARED
        wrapResolver.cpp
        wrapResolverContext.cpp
        wrapResolverTokens.cpp
        module.cpp
        moduleDeps.cpp
)
set_boost_namespace(${AR_PYTHONRESOLVER_TARGET_PYTHON})
# Libs
target_link_libraries(${AR_PYTHONRESOLVER_TARGET_PYTHON}
    ${AR_PYTHONRESOLVER_TARGET_LIB}
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_PYTHONRESOLVER_TARGET_PYTHON}
    PUBLIC
        ${AR_BOOST_INCLUDE_DIR}
        ${AR_PYTHON_INCLUDE_DIR}
        ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_PYTHONRESOLVER_TARGET_PYTHON} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_PYTHONRESOLVER_TARGET_PYTHON}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_PYTHONRESOLVER_USD_PLUGIN_NAME}
        MFB_PACKAGE_MODULE=${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME}
        AR_ENV_SEARCH_PATHS=${AR_ENV_SEARCH_PATHS}
        AR_ENV_SEARCH_REGEX_EXPRESSION=${AR_ENV_SEARCH_REGEX_EXPRESSION}
        AR_ENV_SEARCH_REGEX_FORMAT=${AR_ENV_SEARCH_REGEX_FORMAT}
        AR_PYTHONRESOLVER_USD_PLUGIN_NAME=${AR_PYTHONRESOLVER_USD_PLUGIN_NAME}
        AR_PYTHONRESOLVER_USD_PYTHON_MODULE_FULLNAME=${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_FULLNAME}
        AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME=${AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}
)
# Install
install (
    FILES __init__.py
    DESTINATION lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME}
)
install (
    FILES ${AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME}.py
    DESTINATION lib/python
)
install(
    TARGETS ${AR_PYTHONRESOLVER_TARGET_PYTHON}
    DESTINATION lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME}
)

### Status ###
message(STATUS "--- Usd Python Resolver Instructions Start ---")
message(NOTICE "To use the compiled files, set the following environment variables:")
message(NOTICE "export PATH={AR_HOUDINI_ROOT}/python/bin:${PATH}")
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python:${AR_PYTHON_LIB_SITEPACKAGES}:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/resources:$PXR_PLUGINPATH_NAME")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH")
message(STATUS "--- Usd Python Resolver Instructions End ---\n")





