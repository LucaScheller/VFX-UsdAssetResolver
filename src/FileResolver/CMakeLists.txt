### CPP Settings ###
# Preprocessor Defines (Same as #define)
# This is a hacky way of preprocessing the class name to a custom name.
# It is not advised to do this in a production setup! (https://stackoverflow.com/questions/20979584)
# add_compile_definitions(FileResolver=${AR_FILERESOLVER_USD_CXX_CLASS_NAME})
if (WIN32)
    add_compile_definitions(AR_FILERESOLVER_EXPORTS)
endif()

### Targets ###
## Target library > fileResolver ##
add_library(${AR_FILERESOLVER_TARGET_LIB}
    SHARED
        debugCodes.cpp
        resolver.cpp
        resolverContext.cpp
        resolverTokens.cpp
)
set_boost_namespace(${AR_FILERESOLVER_TARGET_LIB})
# Libs
target_link_libraries(${AR_FILERESOLVER_TARGET_LIB}
    ${AR_PXR_LIB_PREFIX}arch
    ${AR_PXR_LIB_PREFIX}tf
    ${AR_PXR_LIB_PREFIX}gf
    ${AR_PXR_LIB_PREFIX}vt
    ${AR_PXR_LIB_PREFIX}ar
    ${AR_PXR_LIB_PREFIX}sdf
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_FILERESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_FILERESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_FILERESOLVER_TARGET_LIB}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_FILERESOLVER_USD_PLUGIN_NAME}
        AR_ENV_SEARCH_PATHS=${AR_ENV_SEARCH_PATHS}
        AR_ENV_SEARCH_REGEX_EXPRESSION=${AR_ENV_SEARCH_REGEX_EXPRESSION}
        AR_ENV_SEARCH_REGEX_FORMAT=${AR_ENV_SEARCH_REGEX_FORMAT}
)
# Install
configure_file(plugInfo.json.in plugInfo.json)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json DESTINATION ${AR_FILERESOLVER_USD_PLUGIN_NAME}/resources)
install(TARGETS ${AR_FILERESOLVER_TARGET_LIB} DESTINATION ${AR_FILERESOLVER_USD_PLUGIN_NAME}/lib)

## Target library > fileResolver Python ##
add_library(${AR_FILERESOLVER_TARGET_PYTHON}
    SHARED
        module.cpp
        moduleDeps.cpp
        resolverTokens.cpp
        wrapResolver.cpp
        wrapResolverContext.cpp
        wrapResolverTokens.cpp
)
add_dependencies(${AR_FILERESOLVER_TARGET_PYTHON} ${AR_FILERESOLVER_TARGET_LIB})
set_boost_namespace(${AR_FILERESOLVER_TARGET_PYTHON})
# Libs
target_link_libraries(${AR_FILERESOLVER_TARGET_PYTHON}
    ${AR_FILERESOLVER_TARGET_LIB}
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_FILERESOLVER_TARGET_PYTHON}
    PUBLIC
        ${AR_BOOST_INCLUDE_DIR}
        ${AR_PYTHON_INCLUDE_DIR}
        ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_FILERESOLVER_TARGET_PYTHON} PROPERTIES PREFIX "")
if (WIN32)
    set_target_properties(${AR_FILERESOLVER_TARGET_PYTHON} PROPERTIES SUFFIX ".pyd")
endif()
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_FILERESOLVER_TARGET_PYTHON}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_FILERESOLVER_USD_PLUGIN_NAME}
        MFB_PACKAGE_MODULE=${AR_FILERESOLVER_USD_PYTHON_MODULE_NAME}
        AR_ENV_SEARCH_PATHS=${AR_ENV_SEARCH_PATHS}
        AR_ENV_SEARCH_REGEX_EXPRESSION=${AR_ENV_SEARCH_REGEX_EXPRESSION}
        AR_ENV_SEARCH_REGEX_FORMAT=${AR_ENV_SEARCH_REGEX_FORMAT}
        AR_FILERESOLVER_USD_PLUGIN_NAME=${AR_FILERESOLVER_USD_PLUGIN_NAME}
        AR_FILERESOLVER_USD_PYTHON_MODULE_FULLNAME=${AR_FILERESOLVER_USD_PYTHON_MODULE_FULLNAME}
)
# Install
install (
    FILES __init__.py
    DESTINATION ${AR_FILERESOLVER_USD_PLUGIN_NAME}/lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_FILERESOLVER_USD_PYTHON_MODULE_NAME}
)
install(
    TARGETS ${AR_FILERESOLVER_TARGET_PYTHON}
    DESTINATION ${AR_FILERESOLVER_USD_PLUGIN_NAME}/lib/python/${AR_RESOLVER_USD_PYTHON_MODULE_NAME}/${AR_FILERESOLVER_USD_PYTHON_MODULE_NAME}
)

### Tests ###
set(TESTS_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/testenv)
set(TESTS_ENV_PYTHONPATH "PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python:${AR_PYTHON_LIB_SITEPACKAGES}")
set(TESTS_ENV_PXR_PLUGINPATH_NAME "PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/resources")
set(TESTS_ENV_LD_LIBRARY_PATH "LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib:$ENV{HFS}/python/lib:$ENV{HFS}/dsolib")
set(TESTS_ENV_AR_SEARCH_PATHS "AR_SEARCH_PATHS=/env/search/pathA:/env/search/pathB")
set(TESTS_ENV_AR_SEARCH_REGEX_EXPRESSION "AR_SEARCH_REGEX_EXPRESSION=(v\\d\\d\\d)")
set(TESTS_ENV_AR_SEARCH_REGEX_FORMAT "AR_SEARCH_REGEX_FORMAT=v000")
set(TESTS_PYTHON_COMMAND $ENV{HFS}/python/bin/python -B -m unittest discover ${TESTS_SOURCE_DIR})

add_test(
    NAME testFileResolver
    COMMAND ${CMAKE_COMMAND} -E env ${TESTS_ENV_LD_LIBRARY_PATH} ${TESTS_ENV_PYTHONPATH} ${TESTS_ENV_PXR_PLUGINPATH_NAME} ${TESTS_ENV_AR_SEARCH_PATHS} ${TESTS_ENV_AR_SEARCH_REGEX_EXPRESSION} ${TESTS_ENV_AR_SEARCH_REGEX_FORMAT} ${TESTS_PYTHON_COMMAND}
)