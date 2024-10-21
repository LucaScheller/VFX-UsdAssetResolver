### Configuration ###
set(AR_PROJECT_NAME UsdAssetResolver)
set(AR_RESOLVER_USD_PYTHON_MODULE_NAME usdAssetResolver)

function(check_glibcxx_use_cxx11_abi dso_file result_var)
    # Use the readelf command to list the symbols from the DSO file
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E env LC_ALL=C readelf -Ws ${dso_file}
        OUTPUT_VARIABLE readelf_output
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    # Define patterns to match symbols that indicate the use of the new or old ABI
    set(abi_new_pattern "B5cxx11")


    # Check if the symbols contain the new ABI pattern
    if (readelf_output MATCHES ${abi_new_pattern})
        set(${result_var} 1 PARENT_SCOPE)
    else ()
        set(${result_var} 0 PARENT_SCOPE)
    endif ()
endfunction()

if(DEFINED ENV{HOUDINI_NETWORK_DIR})
	set(AR_DIST_NAME houdini)	
elseif(DEFINED ENV{MAYAUSD_NETWORK_DIR})
	set(AR_DIST_NAME maya)	
else()
	set(AR_DIST_NAME usd)
endif()
set(CMAKE_INSTALL_PREFIX "${CMAKE_SOURCE_DIR}/dist/${AR_DIST_NAME}" CACHE PATH "Default install dir")

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

# USD
if ("${AR_DIST_NAME}" STREQUAL "houdini")
	
	set(AR_HOUDINI_ROOT $ENV{HOUDINI_NETWORK_DIR} CACHE PATH "Houdini install directory")
	set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)
	set(AR_PXR_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR})
	if (WIN32)
	    set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/custom/houdini/dsolib)
	    set(AR_PXR_LIB_PREFIX "libpxr_")
	else()
	    set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
	    set(AR_PXR_LIB_PREFIX "pxr_")
    endif()
elseif ("${AR_DIST_NAME}" STREQUAL "maya")
	set(AR_MAYA_ROOT_DIR $ENV{MAYA_NETWORK_DIR} CACHE PATH "Maya install directory")
	set(AR_MAYAUSD_ROOT $ENV{MAYAUSD_NETWORK_DIR}/mayausd CACHE PATH "MayaUSD install directory")
	set(AR_MAYA_INCLUDE_DIR ${AR_MAYA_ROOT_DIR}/include)
	set(AR_PXR_INCLUDE_DIR ${AR_MAYAUSD_ROOT}/USD/include)
	set(AR_PXR_LIB_DIR ${AR_MAYAUSD_ROOT}/USD/lib)
	if (WIN32)
    	set(AR_PXR_LIB_PREFIX "libusd_")
    	set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/libs)
	else()
    	set(AR_PXR_LIB_PREFIX "usd_")
    	set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/lib)
	endif()	    	
else()
	set(AR_USD_ROOT $ENV{USD_LOCATION} CACHE PATH "USD install directory")
	set(AR_PXR_INCLUDE_DIR ${AR_USD_ROOT}/include)
	set(AR_PXR_LIB_DIR ${AR_USD_ROOT}/lib)
	if (WIN32)
    	set(AR_PXR_LIB_PREFIX "libusd_")
    	set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/libs)
	else()
    	set(AR_PXR_LIB_PREFIX "usd_")
    	set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/lib)
	endif()	
endif()

# Python
set(AR_PYTHON_LIB "python$ENV{REZ_PYTHON_MAJOR_VERSION}.$ENV{REZ_PYTHON_MINOR_VERSION}")
set(AR_PYTHON_LIB_NUMBER "python$ENV{REZ_PYTHON_MAJOR_VERSION}$ENV{REZ_PYTHON_MINOR_VERSION}")
if ("${AR_DIST_NAME}" STREQUAL "houdini")
	if (WIN32)
	    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/libs)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_HOUDINI_ROOT}/${AR_PYTHON_LIB_NUMBER}/lib/site-packages)
	else()
	    set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/python/lib)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
	endif()
	set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/${AR_PYTHON_LIB})
elseif ("${AR_DIST_NAME}" STREQUAL "maya")
	if (WIN32)
	    set(AR_PYTHON_LIB_DIR ${AR_MAYA_ROOT}/${AR_PYTHON_LIB_NUMBER}/libs)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_MAYA_ROOT}/${AR_PYTHON_LIB_NUMBER}/lib/site-packages)
	else()
	    set(AR_PYTHON_LIB_DIR ${AR_MAYA_ROOT_DIR}/lib)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
	endif()
	set(AR_PYTHON_INCLUDE_DIR ${AR_MAYA_INCLUDE_DIR}/Python$ENV{REZ_PYTHON_MAJOR_VERSION}$ENV{REZ_PYTHON_MINOR_VERSION}/Python)		
else()
	set(AR_PYTHON_ROOT $ENV{REZ_PYTHON_ROOT} CACHE PATH "Python install directory")
	if (WIN32)
		set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/lib)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_ROOT}/Lib/site-packages)
	else()
		set(AR_PYTHON_LIB_DIR ${AR_PYTHON_ROOT}/lib)
	    set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
	endif()
	set(AR_PYTHON_INCLUDE_DIR ${AR_PYTHON_ROOT}/include/${AR_PYTHON_LIB})
endif()

# Rodeo: python3.7 has suffix m https://discuss.python.org/t/whats-the-difference-between-python3-7-and-python3-7m/16914
if ("${AR_PYTHON_LIB}" STREQUAL "python3.7")
	set(AR_PYTHON_INCLUDE_DIR ${AR_PYTHON_INCLUDE_DIR}m)
endif()

# Boost
if ("${AR_DIST_NAME}" STREQUAL "houdini")
	set(AR_BOOST_NAMESPACE hboost)
else()
	set(AR_BOOST_NAMESPACE boost)
endif()
if (WIN32)
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER}-mt-x64)
else()
    set(AR_BOOST_PYTHON_LIB ${AR_BOOST_NAMESPACE}_${AR_PYTHON_LIB_NUMBER})
endif()
set(AR_BOOST_INCLUDE_DIR ${AR_PXR_INCLUDE_DIR}/${AR_BOOST_NAMESPACE})

### Init ###
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(${AR_PROJECT_NAME} VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(BUILD_SHARED_LIBS ON)
# Preprocessor Defines (Same as #define)
add_compile_definitions(HBOOST_ALL_NO_LIB BOOST_ALL_NO_LIB)

# check libusd_ar.so to see if was build with _GLIBCXX_USE_CXX11_ABI
set(AR_DSO_FILE ${AR_PXR_LIB_DIR}/lib${AR_PXR_LIB_PREFIX}ar.so)		
set(USES_CXX11_ABI 0)
check_glibcxx_use_cxx11_abi(${AR_DSO_FILE} USES_CXX11_ABI)
add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=${USES_CXX11_ABI})

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