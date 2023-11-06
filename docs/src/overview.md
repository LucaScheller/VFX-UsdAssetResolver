| <img src="https://raw.githubusercontent.com/LucaScheller/VFX-UsdAssetResolver/main/tools/UsdAssetResolver_Logo.svg?token=$(date%20+%s)" width="128"> |  <h1> USD Asset Resolver </h1> |
|--|--|

[![Deploy Documentation to GitHub Pages](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml)
[![Build USD Asset Resolvers against Houdini](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/build_houdini.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/build_houdini.yml)

This repository holds reference implementations for [Usd](https://openusd.org/release/index.html) [asset resolvers](https://openusd.org/release/glossary.html#usdglossary-assetresolution). The resolvers are compatible with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html). As the Usd documentation offers quite a good overview over the overall asset resolution system, we will not be covering it in this repository's documentation. You can find a video tutorial [here](./tutorials.md) (or on [Vimeo](https://vimeo.com/881606494)/[Youtube](https://www.youtube.com/watch?v=y4FjYprM4oA)).


## Installation
To build the various resolvers, follow the instructions in the [install guide](./installation/overview.md). 

```admonish info
This guide currently covers compiling against Houdini on Linux and Windows. Alternatively you can also download a pre-compiled builds on our [release page](https://github.com/LucaScheller/VFX-UsdAssetResolver/releases). To load the resolver, you must specify a few environment variables, see our [environment variables](./resolvers/overview.md#environment-variables) section for more details.
```

```admonish tip
We also offer a quick install method for Houdini that does the download of the compiled resolvers and environment variable setup for you. This is ideal if you want to get your hands dirty right away and you don't have any C++ knowledge or extensive USD developer knowledge. If you are a small studio, you can jump right in and play around with our resolvers and prototype them further to make it fit your production needs. See our [Automatic Installation](./installation/automatic_install.md) section for more information.
```

## Feature Overview
Asset resolvers that can be compiled via this repository:
{{#include ./resolvers/shared_features.md:resolverOverview}}

For more information check out the [building guide](./installation/building.md) as well as the [individual resolvers](./resolvers/overview.md) to see their full functionality.