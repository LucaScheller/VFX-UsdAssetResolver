### Configuration ###
set(AR_PROJECT_NAME UsdAssetResolver)
set(AR_RESOLVER_USD_PYTHON_MODULE_NAME usdAssetResolver)

# Env Vars
set(AR_ENV_SEARCH_PATHS "AR_SEARCH_PATHS")
set(AR_ENV_SEARCH_REGEX_EXPRESSION "AR_SEARCH_REGEX_EXPRESSION")
set(AR_ENV_SEARCH_REGEX_FORMAT "AR_SEARCH_REGEX_FORMAT")

# Tests
# Actual invocation of tests is done via ctest in the build directory
if (NOT WIN32)
    enable_testing()
endif()

# File Resolver
option(AR_FILERESOLVER_BUILD "Build the FileResolver" OFF)
if("$ENV{RESOLVER_NAME}" STREQUAL "fileResolver")
    set(AR_FILERESOLVER_BUILD ON)
endif()
set(AR_FILERESOLVER_USD_PLUGIN_NAME fileResolver)
set(AR_FILERESOLVER_USD_CXX_CLASS_NAME FileResolver)
set(AR_FILERESOLVER_USD_PYTHON_MODULE_NAME FileResolver)
set(AR_FILERESOLVER_USD_PYTHON_MODULE_FULLNAME ${AR_RESOLVER_USD_PYTHON_MODULE_NAME}.${AR_FILERESOLVER_USD_PYTHON_MODULE_NAME})
set(AR_FILERESOLVER_TARGET_LIB fileResolver)
set(AR_FILERESOLVER_TARGET_PYTHON _${AR_FILERESOLVER_TARGET_LIB})
set(AR_FILERESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_FILERESOLVER_USD_PLUGIN_NAME})
# Python Resolver
option(AR_PYTHONRESOLVER_BUILD "Build the PythonResolver" OFF)
if("$ENV{RESOLVER_NAME}" STREQUAL "pythonResolver")
    set(AR_PYTHONRESOLVER_BUILD ON)
endif()
set(AR_PYTHONRESOLVER_USD_PLUGIN_NAME pythonResolver)
set(AR_PYTHONRESOLVER_USD_CXX_CLASS_NAME PythonResolver)
set(AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME PythonResolver)
set(AR_PYTHONRESOLVER_USD_PYTHON_MODULE_FULLNAME ${AR_RESOLVER_USD_PYTHON_MODULE_NAME}.${AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME})
set(AR_PYTHONRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME PythonExpose)
set(AR_PYTHONRESOLVER_TARGET_LIB pythonResolver)
set(AR_PYTHONRESOLVER_TARGET_PYTHON _${AR_PYTHONRESOLVER_TARGET_LIB})
set(AR_PYTHONRESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_PYTHONRESOLVER_USD_PLUGIN_NAME})
# Cached Resolver
option(AR_CACHEDRESOLVER_BUILD "Build the CachedResolver" OFF)
if("$ENV{RESOLVER_NAME}" STREQUAL "cachedResolver")
    set(AR_CACHEDRESOLVER_BUILD ON)
endif()
set(AR_CACHEDRESOLVER_USD_PLUGIN_NAME cachedResolver)
set(AR_CACHEDRESOLVER_USD_CXX_CLASS_NAME CachedResolver)
set(AR_CACHEDRESOLVER_USD_PYTHON_MODULE_NAME CachedResolver)
set(AR_CACHEDRESOLVER_USD_PYTHON_MODULE_FULLNAME ${AR_RESOLVER_USD_PYTHON_MODULE_NAME}.${AR_CACHEDRESOLVER_USD_PYTHON_MODULE_NAME})
set(AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME PythonExpose)
set(AR_CACHEDRESOLVER_TARGET_LIB cachedResolver)
set(AR_CACHEDRESOLVER_TARGET_PYTHON _${AR_CACHEDRESOLVER_TARGET_LIB})
set(AR_CACHEDRESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_CACHEDRESOLVER_USD_PLUGIN_NAME})
set(AR_CACHEDRESOLVER_ENV_CONTEXT_BYPASS "AR_CONTEXT_BYPASS")
set(AR_CACHEDRESOLVER_ENV_CONTEXT_DIRTY "AR_CONTEXT_DIRTY")
# Http Resolver
option(AR_HTTPRESOLVER_BUILD "Build the HttpResolver" OFF)
if("$ENV{RESOLVER_NAME}" STREQUAL "httpResolver")
    set(AR_HTTPRESOLVER_BUILD ON)
endif()
set(AR_HTTPRESOLVER_USD_PLUGIN_NAME httpResolver)
set(AR_HTTPRESOLVER_USD_CXX_CLASS_NAME ArHttp)
set(AR_HTTPRESOLVER_TARGET_LIB httpResolver)
set(AR_HTTPRESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_HTTPRESOLVER_USD_PLUGIN_NAME})


# Arch
if (WIN32)
    set(AR_ARCH_LIB_SUFFIX "dll")
else()
    set(AR_ARCH_LIB_SUFFIX "so")
endif()
# Houdini
set(AR_HOUDINI_ROOT $ENV{HFS})
set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/custom/houdini/dsolib)
set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)
# Usd
if (WIN32)
    set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/custom/houdini/dsolib)
    set(AR_PXR_LIB_PREFIX "libpxr_")
else()
    set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
    set(AR_PXR_LIB_PREFIX "pxr_")
endif()

set(AR_PXR_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR})
# Python
set(AR_PYTHON_LIB python3.9)
set(AR_PYTHON_LIB_NUMBER python39)
if (WIN32)
    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/libs)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/lib/site-packages)
else()
    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/python/lib)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
endif()
set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB})
# Boost
set(AR_BOOST_NAMESPACE hboost)
if (WIN32)
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER}-mt-x64)
else()
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER})
endif()
set(AR_BOOST_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_BOOST_NAMESPACE})

### Init ###
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(${AR_PROJECT_NAME} VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(BUILD_SHARED_LIBS ON)
# Preprocessor Defines (Same as #define)
add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0 HBOOST_ALL_NO_LIB BOOST_ALL_NO_LIB)
if (WIN32)
    add_compile_definitions(NOMINMAX)
endif()
# Compiler Options
# This is the same as set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DHBOOST_ALL_NO_LIB -D_GLIBCXX_USE_CXX11_ABI=0")
if (WIN32)
    add_compile_options(/Zc:inline- /w)
else()
    add_compile_options(-fPIC -Wno-deprecated -Wno-deprecated-declarations -Wno-changes-meaning)
endif()

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
# Python
link_directories(${AR_PYTHON_LIB_DIR})

### Targets ###
## Maintained in this repo
# FileResolver
if(${AR_FILERESOLVER_BUILD})
    add_subdirectory("src/FileResolver")
endif()
# PythonResolver
if(${AR_PYTHONRESOLVER_BUILD})
    add_subdirectory("src/PythonResolver")
endif()
# CachedResolver
if(${AR_CACHEDRESOLVER_BUILD})
    add_subdirectory("src/CachedResolver")
endif()
## Maintained in submodule repos
# HttpResolver
if(${AR_HTTPRESOLVER_BUILD})
    add_subdirectory("src/HttpResolver/wrap")
endif()

# Status
message(STATUS "--- Usd Resolver Instructions Start ---")
message(NOTICE "To use the compiled files, set the following environment variables:")
message(NOTICE "export PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/bin:$ENV{HFS}/python/bin:${PATH}")
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python:${AR_PYTHON_LIB_SITEPACKAGES}:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/resources:$PXR_PLUGINPATH_NAME")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib:$ENV{HFS}/python/lib:$ENV{HFS}/dsolib:$LD_LIBRARY_PATH")
message(STATUS "--- Usd Resolver Instructions End ---\n")