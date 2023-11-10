### Configuration ###
set(AR_PROJECT_NAME UsdAssetResolver)
set(AR_RESOLVER_USD_PYTHON_MODULE_NAME usdAssetResolver)
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/dist" CACHE PATH "Default install dir")

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

# TODO: support build with HOUDINI usd/python

# Usd
set(AR_USD_ROOT $ENV{USD_LOCATION} CACHE PATH "USD install directory")
set(AR_USD_INCLUDE_DIR ${AR_USD_ROOT}/include)
set(AR_PXR_LIB_DIR ${AR_USD_ROOT}/lib)
if (WIN32)
    set(AR_PXR_LIB_PREFIX "libusd_")
else()
    set(AR_PXR_LIB_PREFIX "usd_")
endif()

set(AR_PXR_INCLUDE_DIR ${AR_USD_INCLUDE_DIR})

# Python
set(AR_PYTHON_ROOT $ENV{REZ_PYTHON_ROOT} CACHE PATH "Python install directory")
set(AR_PYTHON_LIB "python$ENV{REZ_PYTHON_MAJOR_VERSION}.$ENV{REZ_PYTHON_MINOR_VERSION}")
set(AR_PYTHON_LIB_NUMBER "python$ENV{REZ_PYTHON_MAJOR_VERSION}$ENV{REZ_PYTHON_MINOR_VERSION}")
if (WIN32)
    set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/libs)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_ROOT}/Lib/site-packages)
else()
    set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/lib)
    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
endif()
# Rodeo: python3.7 has suffix m https://discuss.python.org/t/whats-the-difference-between-python3-7-and-python3-7m/16914
set(AR_PYTHON_INCLUDE_DIR ${AR_PYTHON_ROOT}/include/${AR_PYTHON_LIB})
if ("${AR_PYTHON_LIB}" STREQUAL "python3.7")
	set(AR_PYTHON_INCLUDE_DIR ${AR_PYTHON_INCLUDE_DIR}m)
endif()

# Boost
set(AR_BOOST_NAMESPACE boost)
if (WIN32)
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER}-mt-x64)
else()
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER})
endif()
set(AR_BOOST_INCLUDE_DIR ${AR_USD_INCLUDE_DIR}/${AR_BOOST_NAMESPACE})

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
# Usd
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