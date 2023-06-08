### Targets ###
## Target library > PYTHONRESOLVER ##
add_library(${AR_PYTHONRESOLVER_TARGET_LIB}
    SHARED
    ${CMAKE_SOURCE_DIR}/src/utils/boost_include_wrapper.h
    ${CMAKE_CURRENT_LIST_DIR}/resolver.cpp
    ${CMAKE_CURRENT_LIST_DIR}/resolverContext.cpp
)
set_boost_namespace(${AR_PYTHONRESOLVER_TARGET_LIB})
# Props
# Remove default "lib" prefix
set_target_properties(${AR_PYTHONRESOLVER_TARGET_LIB} PROPERTIES PREFIX "")
# USD Plugins use this as the internal plugin name
target_compile_definitions(${AR_PYTHONRESOLVER_TARGET_LIB} PRIVATE MFB_PACKAGE_NAME=${AR_PYTHONRESOLVER_TARGET_LIB})
# Libs
target_link_libraries(${AR_PYTHONRESOLVER_TARGET_LIB}
                      ${AR_PXR_LIB_PREFIX}arch.so
                      ${AR_PXR_LIB_PREFIX}tf.so
                      ${AR_PXR_LIB_PREFIX}gf.so
                      ${AR_PXR_LIB_PREFIX}js.so
                      ${AR_PXR_LIB_PREFIX}vt.so
                      ${AR_PXR_LIB_PREFIX}ar.so
                      ${AR_PYTHON_LIB}
                      ${AR_BOOST_PYTHON_LIB})
# Headers
target_include_directories(${AR_PYTHONRESOLVER_TARGET_LIB}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
)
# Install
configure_file(${CMAKE_CURRENT_LIST_DIR}/plugInfo.json.in ${CMAKE_BINARY_DIR}/plugInfo.json)
install(FILES ${PROJECT_BINARY_DIR}/plugInfo.json DESTINATION ${AR_PYTHONRESOLVER_INSTALL_PREFIX}/resources)
install(FILES ${CMAKE_CURRENT_LIST_DIR}/__init__.py DESTINATION ${AR_PYTHONRESOLVER_INSTALL_PREFIX}/lib/python/${AR_USD_PYTHON_MODULE_NAME})
install(TARGETS ${AR_PYTHONRESOLVER_TARGET_LIB} DESTINATION ${AR_PYTHONRESOLVER_INSTALL_PREFIX}/lib)

## Target library > PYTHONRESOLVER Python ##
add_library(${AR_PYTHONRESOLVER_TARGET_PYTHON}
    SHARED
    ${CMAKE_SOURCE_DIR}/src/utils/boost_include_wrapper.h
    ${CMAKE_CURRENT_LIST_DIR}/wrapResolverContext.cpp
    ${CMAKE_CURRENT_LIST_DIR}/module.cpp
    ${CMAKE_CURRENT_LIST_DIR}/moduleDeps.cpp
)
set_boost_namespace(${AR_PYTHONRESOLVER_TARGET_PYTHON})
# Props
# Remove default "lib" prefix
set_target_properties(${AR_PYTHONRESOLVER_TARGET_PYTHON} PROPERTIES PREFIX "")
# USD Plugins use this as the internal plugin name
target_compile_definitions(${AR_PYTHONRESOLVER_TARGET_PYTHON} PRIVATE
    MFB_PACKAGE_NAME=${AR_PYTHONRESOLVER_USD_PLUGIN_NAME}
    MFB_PACKAGE_MODULE=${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME}
)
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
# Install
install(TARGETS ${AR_PYTHONRESOLVER_TARGET_PYTHON} DESTINATION ${AR_PYTHONRESOLVER_INSTALL_PREFIX}/lib/python/${AR_USD_PYTHON_MODULE_NAME})

## Target Executable > cPythonCall ##
#add_executable(testResolve ${CMAKE_CURRENT_LIST_DIR}/testResolve.cpp)
# Props
#set_target_properties(testResolve PROPERTIES PREFIX "")
# Libs
#target_link_libraries(testResolve PUBLIC ${AR_PYTHON_LIB} ${AR_BOOST_PYTHON_LIB} pxr_usd pxr_tf pxr_vt pxr_arch pxr_sdf pxr_usdGeom tbb)
# Headers
#target_include_directories(testResolve PUBLIC ${AR_PYTHON_INCLUDE_DIR} ${AR_PXR_INCLUDE_DIR})
# Install
#install(TARGETS testResolve DESTINATION ${AR_PYTHONRESOLVER_INSTALL_PREFIX}/bin)


### Status ###
message(STATUS "--- Usd Python Resolver Instructions Start ---")
message(NOTICE "To use the compiled files, set the following environment variables:")
message(NOTICE "export PATH=/opt/hfs19.5/python/bin:${PATH}")
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/${AR_PYTHONRESOLVER_INSTALL_PREFIX}/lib/python:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/${AR_PYTHONRESOLVER_INSTALL_PREFIX}/resources:$PXR_PLUGINPATH_NAME")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/${AR_PYTHONRESOLVER_INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH")
message(NOTICE "To test if it worked, run: ${CMAKE_INSTALL_PREFIX}/${AR_PYTHONRESOLVER_INSTALL_PREFIX}/bin/cPythonCall")
message(STATUS "--- Usd Python Resolver Instructions End ---\n")







