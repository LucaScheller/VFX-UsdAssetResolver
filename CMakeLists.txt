### Configuration ###
set(AR_PROJECT_NAME UsdAssetResolver)
set(AR_RESOLVER_USD_PYTHON_MODULE_NAME usdAssetResolver)

# Env Vars
set(AR_ENV_SEARCH_PATHS "AR_SEARCH_PATHS")
set(AR_ENV_SEARCH_REGEX_EXPRESSION "AR_SEARCH_REGEX_EXPRESSION")
set(AR_ENV_SEARCH_REGEX_FORMAT "AR_SEARCH_REGEX_FORMAT")

# File Resolver
option(AR_FILERESOLVER_BUILD "Build the FileResolver" OFF)
if($ENV{RESOLVER_NAME} STREQUAL "fileResolver")
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
if($ENV{RESOLVER_NAME} STREQUAL "pythonResolver")
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
# Hybrid Resolver
option(AR_HYBRIDRESOLVER_BUILD "Build the HybridResolver" OFF)
if($ENV{RESOLVER_NAME} STREQUAL "hybridResolver")
    set(AR_HYBRIDRESOLVER_BUILD ON)
endif()
set(AR_HYBRIDRESOLVER_USD_PLUGIN_NAME hybridResolver)
set(AR_HYBRIDRESOLVER_USD_CXX_CLASS_NAME HybridResolver)
set(AR_HYBRIDRESOLVER_USD_PYTHON_MODULE_NAME HybridResolver)
set(AR_HYBRIDRESOLVER_USD_PYTHON_MODULE_FULLNAME ${AR_RESOLVER_USD_PYTHON_MODULE_NAME}.${AR_HYBRIDRESOLVER_USD_PYTHON_MODULE_NAME})
set(AR_HYBRIDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME PythonExpose)
set(AR_HYBRIDRESOLVER_TARGET_LIB hybridResolver)
set(AR_HYBRIDRESOLVER_TARGET_PYTHON _${AR_HYBRIDRESOLVER_TARGET_LIB})
set(AR_HYBRIDRESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_HYBRIDRESOLVER_USD_PLUGIN_NAME})
set(AR_HYBRIDRESOLVER_ENV_CONTEXT_BYPASS "AR_ENV_CONTEXT_BYPASS")
set(AR_HYBRIDRESOLVER_ENV_CONTEXT_DIRTY "AR_ENV_CONTEXT_DIRTY")

# Arch
set(AR_ARCH_LIB_SUFFIX so)
# Houdini
set(AR_HOUDINI_ROOT $ENV{HFS})
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
    add_subdirectory("src/PythonResolver")
endif()
# HybridResolver
if(${AR_HYBRIDRESOLVER_BUILD})
    add_subdirectory("src/HybridResolver")
endif()

# Status
message(STATUS "--- Usd Resolver Instructions Start ---")
message(NOTICE "To use the compiled files, set the following environment variables:")
message(NOTICE "export PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/bin:${HFS}/python/bin:${PATH}")
message(NOTICE "export PYTHONPATH=${CMAKE_INSTALL_PREFIX}/lib/python:${AR_PYTHON_LIB_SITEPACKAGES}:$PYTHONPATH")
message(NOTICE "export PXR_PLUGINPATH_NAME=${CMAKE_INSTALL_PREFIX}/resources:${PXR_PLUGINPATH_NAME}")
message(NOTICE "export LD_LIBRARY_PATH=${CMAKE_INSTALL_PREFIX}/lib:${HFS}/python/lib:${HFS}/dsolib:$LD_LIBRARY_PATH")
message(NOTICE "To test if it worked (Only supported for the 'FileResolver'), run:\nexport ${AR_SEARCH_PATHS}=/some/search/pathA:/some/search/pathB\n${CMAKE_INSTALL_PREFIX}/bin/testResolve")
message(STATUS "--- Usd Resolver Instructions End ---\n")

