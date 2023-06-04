### Configuration ###
set(AR_PROJECT_NAME usdSurvivalGuide)
set(AR_USD_PLUGIN_NAME ${AR_PROJECT_NAME})
set(AR_USD_PYTHON_MODULE_NAME UsdSurvivalGuide)
set(AR_USD_PYTHON_CLASS_NAME UsdResolverExampleResolver)
set(AR_TARGET_RESOLVER ${AR_PROJECT_NAME})
set(AR_TARGET_RESOLVER_PYTHON _${AR_PROJECT_NAME})

# Houdini
set(AR_HOUDINI_ROOT /opt/hfs19.5)
set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)
# Usd
set(AR_PXR_LIB_DIR ${AR_HOUDINI_LIB_DIR})
set(AR_PXR_LIB_PREFIX "libpxr_")
set(AR_PXR_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR})
# Python
set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_LIB_DIR})
set(AR_PYTHON_LIB "${AR_HOUDINI_LIB_DIR}/libhboost_python39.so")
set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/python3.9)
# Boost
set(AR_BOOST_INCLUDE_DIR "${AR_HOUDINI_INCLUDE_DIR}/hboost")


### Init ###
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(usdExampleResolver VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DHBOOST_ALL_NO_LIB -D_GLIBCXX_USE_CXX11_ABI=0 ")
SET(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/dist/${AR_USD_PLUGIN_NAME}/" CACHE PATH "Default install dir " FORCE)
# Mute warnings
add_compile_options(-fPIC -Wno-deprecated) # -Zc:inline-

### Packages ###
# Houdini
# link_directories(${AR_HOUDINI_LIB_DIR})
# Usd (Already provided via Houdini)
link_directories(${AR_PXR_LIB_DIR})
# Python (Already provided via Houdini)
link_directories(${AR_PYTHON_LIB_DIR})

### Targets ###
## Target library > resolver ##
add_library(${AR_TARGET_RESOLVER}
    SHARED
    src/resolver.cpp
    src/resolverContext.cpp
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_TARGET_RESOLVER} PROPERTIES PREFIX "")
# USD Plugins use this as the internal plugin name
target_compile_definitions(${AR_TARGET_RESOLVER} PRIVATE MFB_PACKAGE_NAME=${AR_TARGET_RESOLVER})
# Libs
target_link_libraries(${AR_TARGET_RESOLVER} 
                      ${AR_PXR_LIB_PREFIX}arch.so 
                      ${AR_PXR_LIB_PREFIX}tf.so 
                      ${AR_PXR_LIB_PREFIX}gf.so 
                      ${AR_PXR_LIB_PREFIX}js.so 
                      ${AR_PXR_LIB_PREFIX}vt.so 
                      ${AR_PXR_LIB_PREFIX}ar.so)
# Headers
target_include_directories(${AR_TARGET_RESOLVER}
    PUBLIC
    ${AR_PXR_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
)
# Install
configure_file(src/plugInfo.json.in ${CMAKE_BINARY_DIR}/src/plugInfo.json)
install(FILES ${PROJECT_BINARY_DIR}/src/plugInfo.json DESTINATION resources)
install(FILES src/__init__.py DESTINATION lib/python/${AR_USD_PYTHON_MODULE_NAME})
install(TARGETS ${AR_TARGET_RESOLVER} LIBRARY)


## Target library > resolver python ##
add_library(${AR_TARGET_RESOLVER_PYTHON}
    SHARED
    src/wrapResolverContext.cpp
    src/module.cpp
    src/moduleDeps.cpp
)
# Props
# Remove default "lib" prefix
set_target_properties(${AR_TARGET_RESOLVER_PYTHON} PROPERTIES PREFIX "")
# USD Plugins use this as the internal plugin name
target_compile_definitions(${AR_TARGET_RESOLVER_PYTHON} PRIVATE
    MFB_PACKAGE_NAME=${AR_USD_PLUGIN_NAME}
    MFB_PACKAGE_MODULE=${AR_USD_PYTHON_MODULE_NAME}
)
# Libs
target_link_libraries(${AR_TARGET_RESOLVER_PYTHON}
    ${AR_TARGET_RESOLVER}
    ${AR_PYTHON_LIB}
)
# Headers
target_include_directories(${AR_TARGET_RESOLVER_PYTHON}
    PUBLIC
    ${AR_BOOST_INCLUDE_DIR}
    ${AR_PYTHON_INCLUDE_DIR}
    ${AR_PXR_INCLUDE_DIR}
)
# Install
install(TARGETS ${AR_TARGET_RESOLVER_PYTHON} DESTINATION lib/python/${AR_USD_PYTHON_MODULE_NAME})


### Status ###
message(STATUS "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python:$PYTHONPATH")
message(STATUS "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/resources:$PXR_PLUGINPATH_NAME")
message(STATUS "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH")





