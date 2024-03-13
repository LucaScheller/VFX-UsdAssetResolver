### Configuration ###
set(AR_PROJECT_NAME UsdAssetResolver)
set(AR_RESOLVER_USD_PYTHON_MODULE_NAME usdAssetResolver)
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/dist" CACHE PATH "Default install dir")

# AR Spec Version
# Make sure to set this to the same value that 'AR_VERSION' was set to if you are building
# USD versions that can use both spec versions. For more info, see https://openusd.org/release/wp_ar2.html.
# This needs to be overriden per DCC below.
set(AR_SPEC_VERSION 0)

# Env Vars
set(AR_ENV_SEARCH_PATHS "AR_SEARCH_PATHS" CACHE STRING "Environment variable that holds the search path(s) for non absolute asset paths.")
set(AR_ENV_SEARCH_REGEX_EXPRESSION "AR_SEARCH_REGEX_EXPRESSION" CACHE STRING "Environment variable that holds the regex to preformat asset paths before mapping them via the mapping pairs.")
set(AR_ENV_SEARCH_REGEX_FORMAT "AR_SEARCH_REGEX_FORMAT" CACHE STRING "Environment variable that holds the string to replace with what was found by the regex expression.")

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
set(AR_CACHEDRESOLVER_ENV_EXPOSE_RELATIVE_PATH_IDENTIFIERS "AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS" CACHE STRING "Environment variable that controls if relative path identifiers should be Python exposed.")

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
set(AR_HOUDINI_ROOT $ENV{HFS} CACHE PATH "Houdini install directory")
if (WIN32)
    set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/custom/houdini/dsolib)
else()
    set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
endif()
set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)

set(AR_SPEC_VERSION 2)
file(REAL_PATH ${AR_HOUDINI_ROOT} AR_HOUDINI_ROOT_RESOLVED)
string(FIND ${AR_HOUDINI_ROOT_RESOLVED} "19.0" AR_HOUDINI_ROOT_IS_H190)
if (${AR_HOUDINI_ROOT_IS_H190} STREQUAL "-1")
    add_compile_definitions(AR_SPEC_VERSION=2)
    add_compile_definitions(AR_VERSION=2)
else()
    message("Houdini 19.0 detected, switching to AR_SPEC_VERSION=1")
    add_compile_definitions(AR_SPEC_VERSION=1)
    add_compile_definitions(AR_VERSION=1)
endif()
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
if (WIN32)
    if(EXISTS "${AR_HOUDINI_ROOT}/python310")
        set(AR_PYTHON_LIB python3.10)
        set(AR_PYTHON_LIB_NUMBER python310)
    elseif(EXISTS "${AR_HOUDINI_ROOT}/python39")
        set(AR_PYTHON_LIB python3.9)
        set(AR_PYTHON_LIB_NUMBER python39)
    elseif(EXISTS "${AR_HOUDINI_ROOT}/python37")
        set(AR_PYTHON_LIB python3.7)
        set(AR_PYTHON_LIB_NUMBER python37)
    else()
        message(FATAL_ERROR "Failed to find valid Python version.")
    endif()
else()
    if(EXISTS "${AR_HOUDINI_ROOT}/python/bin/python3.10")
        set(AR_PYTHON_LIB python3.10)
        set(AR_PYTHON_LIB_NUMBER python310)
    elseif(EXISTS "${AR_HOUDINI_ROOT}/python/bin/python3.9")
        set(AR_PYTHON_LIB python3.9)
        set(AR_PYTHON_LIB_NUMBER python39)
    elseif(EXISTS "${AR_HOUDINI_ROOT}/python/bin/python3.7")
        set(AR_PYTHON_LIB python3.7)
        set(AR_PYTHON_LIB_NUMBER python37)
    else()
        message(FATAL_ERROR "Failed to find valid Python version.")
    endif()
endif()

if (WIN32)
    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/libs)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/lib/site-packages)
    set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB})
else()
    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/python/lib)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
    if(EXISTS "${AR_HOUDINI_ROOT}/python/include/${AR_PYTHON_LIB}")
        set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB})
    elseif(EXISTS "${AR_HOUDINI_ROOT}/python/include/${AR_PYTHON_LIB}m")
        set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB}m)
    endif()
endif()
# Boost
set(AR_BOOST_NAMESPACE hboost)
if (WIN32)
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER}-mt-x64)
else()
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER})
endif()
set(AR_BOOST_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_BOOST_NAMESPACE})

### Init ###
cmake_minimum_required(VERSION 3.19 FATAL_ERROR)
project(${AR_PROJECT_NAME} VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(BUILD_SHARED_LIBS ON)
# Preprocessor Defines (Same as #define)
add_compile_definitions(HBOOST_ALL_NO_LIB BOOST_ALL_NO_LIB)
if (WIN32)
    add_compile_definitions(NOMINMAX)
else()
    # Notes:
    # Houdini 20 - Switched to the new C++11 ABI for Linux https://www.sidefx.com/docs/houdini/news/20/platforms.html
    # For Houdini versions that use gcc 9.3, please set this to _GLIBCXX_USE_CXX11_ABI=0
    file(REAL_PATH ${AR_HOUDINI_ROOT} AR_HOUDINI_ROOT_RESOLVED)
    string(FIND ${AR_HOUDINI_ROOT_RESOLVED} "19.5" AR_HOUDINI_ROOT_IS_H195)
    if (${AR_HOUDINI_ROOT_IS_H195} STREQUAL "-1")
        add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=1)
    else()
        message("Houdini 19.5 detected, switching to _GLIBCXX_USE_CXX11_ABI=0")
        add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0)
    endif()
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
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/<resolverName>/lib/python:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/<resolverName>/resources:$PXR_PLUGINPATH_NAME")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/<resolverName>/lib:$LD_LIBRARY_PATH")
message(STATUS "--- Usd Resolver Instructions End ---\n")