# Usd Asset Resolver
[![Deploy Documentation to GitHub Pages](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml)

This repository holds reference implementations for [Usd](https://openusd.org/release/index.html) [asset resolvers](https://openusd.org/release/glossary.html#usdglossary-assetresolution). The resolvers are compatible with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html). As the Usd documentation offers quite a good overview over the overall asset resolution system, we will not be covering it in this repostories documentation.



# Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Resolvers](#resolvers)
4. [Example stage and mapping pair files](#example-stage-and-mapping-pair-files)
# Features

All resolvers share these common feautures:
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the ```Resolver.CreateDefaultContextForAsset``` [(Docs)](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)

Asset resolvers that can be compiled via this repository:
- **File Resolver** - A file system based resolver similiar to the default resolver with support for custom mapping pairs.
    - A simple mapping pair look up in a provided mapping pair Usd file. The mapping data has to stored in the Usd layer metadata in an key called ```mappingPairs``` as an array with the syntax ```["sourcePathA.usd", "targetPathA.usd", "sourcePathB.usd", "targetPathB.usd"]```. (This is quite similar to Rodeo's asset resolver that can be found [here](https://github.com/rodeofx/rdo_replace_resolver) using the AR 1.0 specification.)
    - You can use the ```AR_ENV_SEARCH_REGEX_EXPRESSION```/```AR_ENV_SEARCH_REGEX_FORMAT``` environment variables to preformat any asset paths before they looked up in the ```mappingPairs```. The regex match found by the ```AR_ENV_SEARCH_REGEX_EXPRESSION``` environment variable will be replaced by the content of the  ```AR_ENV_SEARCH_REGEX_FORMAT``` environment variable. The environment variable names can be customized in the [CMakeLists.txt](CMakeLists.txt) file.
    - You can adjust the resolver context content during runtime via exposed Python methods (More info below). Refreshing the stage is also supported, although it might be required to trigger additional reloads in certain DCCs.
- **Python Resolver** - Python based implemention of the file resolver:
    - This resolver has feature parity to the file resolver, but the implementation is slightly different. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database related pipelines in Python.
    - Running in Python does not allow proper multithreading due to Python's [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock), so this resolver should not be used in (large scale) productions. 

# Installation
Follow the instructions in the [install.md](install.md) file. We use [CMake](https://cmake.org) as a build system in conjunction with any Houdini version greater than 19.5 for compilation.

> :warning: Currently only building against Linux has been tested.
