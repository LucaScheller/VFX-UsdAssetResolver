# Usd Asset Resolver
[![Deploy Documentation to GitHub Pages](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml)

This repository holds reference implementations for [Usd](https://openusd.org/release/index.html) [asset resolvers](https://openusd.org/release/glossary.html#usdglossary-assetresolution). The resolvers are compatible with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html). As the Usd documentation offers quite a good overview over the overall asset resolution system, we will not be covering it in this repository's documentation.

## Installation
To build the various resolvers, follow the instructions in the [install guide](./installation/overview.md). 

```admonish info
This guide currently covers compiling against Houdini on Linux and Windows. Alternatively you can also download a pre-compiled builds on our [release page](https://github.com/LucaScheller/VFX-UsdAssetResolver/releases). To load the resolver, you must specify a few environment variables, see our [environment variables](./resolvers/overview.md#environment-variables) section for more details.
```

## Feature Overview
Asset resolvers that can be compiled via this repository:
- **File Resolver** - A file system based resolver similar to the default resolver with support for custom mapping pairs as well as at runtime modification and refreshing.
- **Python Resolver** - Python based implementation of the file resolver. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database interactions in Python for initial research.

For more information check out the [building guide](./installation/building.md) as well as the [individual resolvers](./resolvers/overview.md) to see their full functionality.


