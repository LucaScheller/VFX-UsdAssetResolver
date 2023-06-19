# Usd Asset Resolver
[![Deploy Documentation to GitHub Pages](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml)

This repository holds reference implementations for [Usd](https://openusd.org/release/index.html) [asset resolvers](https://openusd.org/release/glossary.html#usdglossary-assetresolution). The resolvers are compatible with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html). As the Usd documentation offers quite a good overview over the overall asset resolution system, we will not be covering it in this repostories documentation.

## Installation
To build the various resolvers, follow the instructions in the [install guide](https://lucascheller.github.io/VFX-UsdAssetResolver/installation/requirements.html). 

```admonish info
Currently this guide only covers building against Houdini on Linux.
```

## Feature Overview

Asset resolvers that can be compiled via this repository:
- **File Resolver** - A file system based resolver similar to the default resolver with support for custom mapping pairs as well as at runtime modification and refreshing.
- **Python Resolver** - Python based implementation of the file resolver. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database interactions in Python.

All resolvers share these common features:
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)

For more information check out the [building guide](https://lucascheller.github.io/VFX-UsdAssetResolver/installation/building.html) as well as the [individual resolvers](https://lucascheller.github.io/VFX-UsdAssetResolver/resolvers/overview.html) to see their full functionality.


