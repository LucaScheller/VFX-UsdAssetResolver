### Targets ###
## Target library > FileResolver ##
add_library(${AR_FILERESOLVER_TARGET_LIB}
    SHARED
    ${CMAKE_CURRENT_LIST_DIR}/resolver.cpp
    ${CMAKE_CURRENT_LIST_DIR}/resolverContext.cpp
)
set_boost_namespace(${AR_FILERESOLVER_TARGET_LIB})
# Props
# Remove default "lib" prefix
set_target_properties(${AR_FILERESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_FILERESOLVER_TARGET_LIB}
                           PRIVATE
                           # USD Plugins use this as the internal plugin name
                           MFB_PACKAGE_NAME=${AR_FILERESOLVER_USD_PLUGIN_NAME} 
                           # Hacky Way to Replace Class Name https://stackoverflow.com/questions/20979584
                           # FileResolver=${AR_FILERESOLVER_USD_CXX_CLASS_NAME}
)
# Libs
target_link_libraries(${AR_FILERESOLVER_TARGET_LIB}
                      ${AR_PXR_LIB_PREFIX}arch.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PXR_LIB_PREFIX}tf.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PXR_LIB_PREFIX}gf.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PXR_LIB_PREFIX}js.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PXR_LIB_PREFIX}vt.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PXR_LIB_PREFIX}ar.${AR_ARCH_LIB_SUFFIX}
                      ${AR_PYTHON_LIB})
# Headers
target_include_directories(${AR_FILERESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
)
# Install
configure_file(${CMAKE_CURRENT_LIST_DIR}/plugInfo.json.in ${CMAKE_BINARY_DIR}/plugInfo.json)
install(FILES ${PROJECT_BINARY_DIR}/plugInfo.json DESTINATION ${AR_FILERESOLVER_INSTALL_PREFIX}/resources)
install(FILES ${CMAKE_CURRENT_LIST_DIR}/__init__.py DESTINATION ${AR_FILERESOLVER_INSTALL_PREFIX}/lib/python/${AR_USD_PYTHON_MODULE_NAME})
install(TARGETS ${AR_FILERESOLVER_TARGET_LIB} DESTINATION ${AR_FILERESOLVER_INSTALL_PREFIX}/lib)

## Target library > FileResolver Python ##
add_library(${AR_FILERESOLVER_TARGET_PYTHON}
    SHARED
    ${CMAKE_CURRENT_LIST_DIR}/wrapResolverContext.cpp
    ${CMAKE_CURRENT_LIST_DIR}/module.cpp
    ${CMAKE_CURRENT_LIST_DIR}/moduleDeps.cpp
)
set_boost_namespace(${AR_FILERESOLVER_TARGET_PYTHON})
# Props
# Remove default "lib" prefix
set_target_properties(${AR_FILERESOLVER_TARGET_PYTHON} PROPERTIES PREFIX "")
# Preprocessor Defines (Same as #define)
target_compile_definitions(${AR_FILERESOLVER_TARGET_PYTHON} 
    PRIVATE
    # USD Plugins use this as the internal plugin name
    MFB_PACKAGE_NAME=${AR_FILERESOLVER_USD_PLUGIN_NAME}
    MFB_PACKAGE_MODULE=${AR_FILERESOLVER_USD_PYTHON_MODULE_NAME}
    # Hacky Way to Replace Class Name https://stackoverflow.com/questions/20979584
    # FileResolver=${AR_FILERESOLVER_USD_CXX_CLASS_NAME}
)
# Libs
target_link_libraries(${AR_FILERESOLVER_TARGET_PYTHON}
    ${AR_FILERESOLVER_TARGET_LIB}
    ${AR_BOOST_PYTHON_LIB}
)
message(WARNING ${AR_BOOST_PYTHON_LIB})
# Headers
target_include_directories(${AR_FILERESOLVER_TARGET_PYTHON}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Install
install(TARGETS ${AR_FILERESOLVER_TARGET_PYTHON} DESTINATION ${AR_FILERESOLVER_INSTALL_PREFIX}/lib/python/${AR_USD_PYTHON_MODULE_NAME})

## Target Executable > cPythonCall ##
add_executable(testResolve ${CMAKE_CURRENT_LIST_DIR}/testResolve.cpp)
# Props
set_target_properties(testResolve PROPERTIES PREFIX "")
# Libs
target_link_libraries(testResolve PUBLIC
                     ${AR_PYTHON_LIB}
                     ${AR_BOOST_PYTHON_LIB}
                     pxr_usd pxr_tf pxr_vt pxr_arch pxr_sdf pxr_usdGeom tbb)
# Headers
target_include_directories(testResolve PUBLIC ${AR_PYTHON_INCLUDE_DIR} ${AR_PXR_INCLUDE_DIR})
# Install
install(TARGETS testResolve DESTINATION ${AR_FILERESOLVER_INSTALL_PREFIX}/bin)


### Status ###
message(STATUS "--- Usd File Resolver Instructions Start ---")
message(NOTICE "To use the compiled files, set the following environment variables:")
message(NOTICE "export PATH=${CMAKE_INSTALL_PREFIX}/${AR_FILERESOLVER_INSTALL_PREFIX}/bin:/opt/hfs19.5/python/bin:$PATH")
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/${AR_FILERESOLVER_INSTALL_PREFIX}/lib/python:${AR_PYTHON_LIB_SITEPACKAGES}:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/${AR_FILERESOLVER_INSTALL_PREFIX}/resources:$PXR_PLUGINPATH_NAME")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/${AR_FILERESOLVER_INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH")
message(NOTICE "To test if it worked, run: ${CMAKE_INSTALL_PREFIX}/${AR_FILERESOLVER_INSTALL_PREFIX}/bin/cPythonCall")
message(STATUS "--- Usd File Resolver Instructions End ---\n")
