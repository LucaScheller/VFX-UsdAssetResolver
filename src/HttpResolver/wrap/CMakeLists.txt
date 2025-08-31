### CPP Settings ###
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
# Libs
target_link_libraries(${AR_HTTPRESOLVER_TARGET_LIB}
    ${AR_PYTHON_LIB}
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
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
    ${AR_BOOST_INCLUDE_DIR}
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
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/plugInfo.json DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/resources)
install(TARGETS ${AR_HTTPRESOLVER_TARGET_LIB} DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/lib)
# Demo
set(_server_permissions OWNER_EXECUTE OWNER_WRITE OWNER_READ GROUP_READ GROUP_WRITE GROUP_EXECUTE WORLD_READ WORLD_WRITE WORLD_EXECUTE)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../arHttp/src/arHttpSampleServer DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/demo/packages)
if (WIN32)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/server_install.bat PERMISSIONS ${_server_permissions} DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/demo)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/server_launch.bat PERMISSIONS ${_server_permissions} DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/demo)
else()
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/server_install.sh PERMISSIONS ${_server_permissions} DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/demo)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/server_launch.sh PERMISSIONS ${_server_permissions} DESTINATION ${AR_HTTPRESOLVER_USD_PLUGIN_NAME}/demo)
endif()
