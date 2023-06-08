### Configuration ###
set(AR_PROJECT_NAME usdSurvivalGuide)

set(AR_FILERESOLVER_USD_PLUGIN_NAME FileResolver)
set(AR_FILERESOLVER_USD_PYTHON_MODULE_NAME UsdSurvivalGuide)
set(AR_FILERESOLVER_USD_PYTHON_CLASS_NAME UsdResolverExampleResolver)
set(AR_FILERESOLVER_TARGET_LIB FileResolver)
set(AR_FILERESOLVER_TARGET_PYTHON _FileResolver)
set(AR_FILERESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_FILERESOLVER_USD_PLUGIN_NAME})

set(AR_PYTHONRESOLVER_USD_PLUGIN_NAME PythonResolver)
set(AR_PYTHONRESOLVER_USD_PYTHON_MODULE_NAME UsdSurvivalGuide)
set(AR_PYTHONRESOLVER_USD_PYTHON_CLASS_NAME UsdResolverExampleResolver)
set(AR_PYTHONRESOLVER_TARGET_LIB PythonResolver)
set(AR_PYTHONRESOLVER_TARGET_PYTHON _PythonResolver)
set(AR_PYTHONRESOLVER_INSTALL_PREFIX ${AR_PROJECT_NAME}/${AR_PYTHONRESOLVER_USD_PLUGIN_NAME})

# Houdini
set(AR_HOUDINI_ROOT /opt/hfs19.5)
set(AR_HOUDINI_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
set(AR_HOUDINI_INCLUDE_DIR ${AR_HOUDINI_ROOT}/toolkit/include)
# Usd
set(AR_PXR_LIB_DIR ${AR_HOUDINI_ROOT}/dsolib)
set(AR_PXR_LIB_PREFIX "libpxr_")
set(AR_PXR_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR})
# Python
set(AR_PYTHON_LIB_DIR ${AR_HOUDINI_ROOT}/python/lib)
set(AR_PYTHON_LIB python3.9)
set(AR_PYTHON_LIB_SITEPACKAGES ${AR_PYTHON_LIB_DIR}/${AR_PYTHON_LIB}/site-packages)
set(AR_PYTHON_INCLUDE_DIR ${AR_HOUDINI_INCLUDE_DIR}/python3.9)
# Boost
set(BOOST_NAMESPACE hboost)
set(AR_BOOST_INCLUDE_DIR "${AR_HOUDINI_INCLUDE_DIR}/hboost")
set(AR_BOOST_PYTHON_LIB hboost_python39)

### Init ###
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(${AR_PROJECT_NAME} VERSION 1.0.0 LANGUAGES CXX)

### CPP Settings ###
set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/bin")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_GLIBCXX_USE_CXX11_ABI=0 ")
SET(CMAKE_INSTALL_PREFIX "${CMAKE_CURRENT_SOURCE_DIR}/dist/" CACHE PATH "Default install dir " FORCE)
set(BUILD_SHARED_LIBS ON)
# Mute warnings
add_definitions(-D_GLIBCXX_USE_CXX11_ABI=0)
add_compile_options(-fPIC -Wno-deprecated -Wno-deprecated-declarations -Wno-changes-meaning ) # -Zc:inline-

### Packages ###
# Defaults
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/defaults)
include(setBoostNamespace)
# Houdini
# link_directories(${AR_HOUDINI_LIB_DIR})
# Usd (Already provided via Houdini)
link_directories(${AR_PXR_LIB_DIR})
# Python (Already provided via Houdini)
link_directories(${AR_PYTHON_LIB_DIR})

### Targets ###
# FileResolver
include("src/FileResolver/FileResolver.cmake")
# PythonResolver
#include("src/PythonResolver/PythonResolver.cmake")