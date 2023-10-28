### CPP Settings ###
SET(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/dist/${AR_HTTPRESOLVER_USD_PLUGIN_NAME}" CACHE PATH "Default install dir " FORCE)

# Preprocessor Defines (Same as #define)
if (WIN32)
    add_compile_definitions(AR_HTTPRESOLVER_EXPORTS)
endif()

### Targets ###
## Target library > httpResolver ##
add_library(${AR_HTTPRESOLVER_TARGET_LIB}
    SHARED
        ../arHttp/src/arHttp/resolver.cpp
)
#set_boost_namespace(${AR_HTTPRESOLVER_TARGET_LIB})
# Libs
target_link_libraries(${AR_HTTPRESOLVER_TARGET_LIB}
    ${AR_PXR_LIB_PREFIX}arch
    ${AR_PXR_LIB_PREFIX}tf
    ${AR_PXR_LIB_PREFIX}gf
    ${AR_PXR_LIB_PREFIX}vt
    ${AR_PXR_LIB_PREFIX}ar
    ${AR_PXR_LIB_PREFIX}sdf
    ${AR_BOOST_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_HTTPRESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_HTTPRESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_HTTPRESOLVER_TARGET_LIB}
    PRIVATE
        # USD Plugin Internal Namings
        MFB_PACKAGE_NAME=${AR_HTTPRESOLVER_USD_PLUGIN_NAME}
)
# Install
configure_file(plugInfo.json.in plugInfo.json)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json DESTINATION resources)
install(TARGETS ${AR_HTTPRESOLVER_TARGET_LIB} RUNTIME DESTINATION lib)