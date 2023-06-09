
### Configuration ###
set(AR_PROJECT_NAME usdExampleResolver)

option(AR_FILERESOLVER_BUILD "Build the FileResolver" ON)
set(AR_FILERESOLVER_USD_PLUGIN_NAME usdResolverExample)
set(AR_FILERESOLVER_USD_CXX_CLASS_NAME UsdResolverExampleResolver)
set(AR_FILERESOLVER_USD_PYTHON_MODULE_NAME UsdResolverExample)
set(AR_FILERESOLVER_TARGET_LIB usdResolverExample)
set(AR_FILERESOLVER_TARGET_PYTHON _usdResolverExample)
set(AR_FILERESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_FILERESOLVER_USD_PLUGIN_NAME})

# Arch
set(AR_ARCH_LIB_SUFFIX so)
# Houdini
set(AR_HOUDINI_ROOT /opt/hfs19.5)
set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)
# Usd
set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
set(AR_PXR_LIB_PREFIX "pxr_")
set(AR_PXR_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR})
# Python
set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/python/lib)
set(AR_PYTHON_LIB python3.9)
set(AR_PYTHON_LIB_NUMBER python39)
set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB})
# Boost
set(AR_BOOST_NAMESPACE hboost)
set(AR_BOOST_INCLUDE_DIR "${AR_HOUDINI_INCLUDE_DIR}/${AR_BOOST_NAMESPACE}")
set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER})

### Init ###
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(${AR_PROJECT_NAME} VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(BUILD_SHARED_LIBS ON)
# Preprocessor Defines (Same as #define)
add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0 HBOOST_ALL_NO_LIB BOOST_ALL_NO_LIB)
# This is the same as set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DHBOOST_ALL_NO_LIB -D_GLIBCXX_USE_CXX11_ABI=0")
# Compiler Options
add_compile_options(-fPIC -Wno-deprecated -Wno-deprecated-declarations -Wno-changes-meaning) # -Zc:inline-

### Packages ###
# Defaults
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/defaults)
# Boost Namespace Wrapper
include(setBoostNamespace)
include_directories(${CMAKE_SOURCE_DIR}/src/utils)
# Houdini
link_directories(${AR_HOUDINI_LIB_DIR})
# Usd (Already provided via Houdini)
link_directories(${AR_PXR_LIB_DIR})
# Python (Already provided via Houdini)
#link_directories(${AR_PYTHON_LIB_DIR})

### Targets ###
# FileResolver
if(${AR_FILERESOLVER_BUILD})
    add_subdirectory("src/FileResolver")
endif()
# PythonResolver
if(${AR_PYTHONRESOLVER_BUILD})
    include("src/PythonResolver")
endif()
