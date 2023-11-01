| <img src="https://raw.githubusercontent.com/LucaScheller/VFX-UsdAssetResolver/main/tools/UsdAssetResolver_Logo.svg" width="128"> |  <h1> OpenUSD Asset Resolver </h1> |
|--|--|

[![Deploy Documentation to GitHub Pages](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/mdbook.yml) [![Build USD Asset Resolvers against Houdini](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/build_houdini.yml/badge.svg)](https://github.com/LucaScheller/VFX-UsdAssetResolver/actions/workflows/build_houdini.yml)

This repository holds reference implementations for [Usd](https://openusd.org/release/index.html) [asset resolvers](https://openusd.org/release/glossary.html#usdglossary-assetresolution). The resolvers are compatible with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html). As the Usd documentation offers quite a good overview over the overall asset resolution system, we will not be covering it in this repository's documentation.

## Installation
To build the various resolvers, follow the instructions in the [install guide](https://lucascheller.github.io/VFX-UsdAssetResolver/installation/requirements.html). 

> [!NOTE]
> This guide currently covers compiling against Houdini on Linux and Windows. Alternatively you can also download a pre-compiled builds on our [release page](https://github.com/LucaScheller/VFX-UsdAssetResolver/releases). To load the resolver, you must specify a few environment variables, see our [environment variables](https://lucascheller.github.io/VFX-UsdAssetResolver/resolvers/overview.html#environment-variables) section for more details.

> [!IMPORTANT]
> We also offer a quick install method for Houdini that does the download of the compiled resolvers and environment variable setup for you. This is ideal if you want to get your hands dirty right away and you don't have any C++ knowledge or extensive USD developer knowledge. If you are a small studio, you can jump right in and play around with our resolvers and prototype them further to make it fit your production needs.

To run the "Update Manager" simply run this snippet in the "Houdini Python Source Editor" panel:

    import urllib,ssl
    update_manager_url = 'https://raw.githubusercontent.com/LucaScheller/VFX-UsdAssetResolver/main/tools/update_manager.py?token=$(date%20+%s)'
    exec(urllib.request.urlopen(update_manager_url,context=ssl._create_unverified_context()).read(), globals(), locals())
    run_houdini()

See our [Automatic Installation](https://lucascheller.github.io/VFX-UsdAssetResolver/installation/automatic_install.html) section for more information.

## Feature Overview
Asset resolvers that can be compiled via this repository:
- **Production Resolvers**
    - **File Resolver** - A file system based resolver similar to the default resolver with support for custom mapping pairs as well as at runtime modification and refreshing.
    - **Cached Resolver** - A resolver that first consults an internal resolver context dependent cache to resolve asset paths. If the asset path is not found in the cache, it will redirect the request to Python and cache the result. This is ideal for smaller studios, as this preserves the speed of C++ with the flexibility of Python.
- **RnD Resolvers**
    - **Python Resolver** - Python based implementation of the file resolver. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database interactions in Python for initial research.
- **Proof Of Concept Resolvers**
    - **Http Resolver** - A proof of concept http resolver. This is kindly provided and maintained by @charlesfleche in the [arHttp: Offloads USD asset resolution to an HTTP server
    ](https://github.com/charlesfleche/arHttp) repository. For documentation, feature suggestions and bug reports, please file a ticket there. This repo handles the auto-compilation against DCCs and exposing to the automatic installation update manager UI.

For more information check out the [building guide](https://lucascheller.github.io/VFX-UsdAssetResolver/installation/building.html) as well as the [individual resolvers](https://lucascheller.github.io/VFX-UsdAssetResolver/resolvers/overview.html) to see their full functionality.

## Contributing and Acknowledgements
Special thanks to [Jonas Sorgenfrei](https://github.com/jonassorgenfrei) for helping bring this project to life as well as all the contributors on the Usd-Interest forum, particularly
Mark Tucker, ColinE, Jake Richards, Pawel Olas, Joshua Miller US, Simon Boorer. 

Post of relevance in the Usd-Interest Forum to this repo:
- [usdResolverExample AR 2.0 for Houdini 19.5](https://groups.google.com/g/usd-interest/c/82GxMaAG1eo/m/ePk2tYptAAAJ)
- [USD Asset Resolver Python](https://groups.google.com/g/usd-interest/c/60e5aQgW_gg/m/DfCcN_1oAwAJ)
- [AR 2.0: CreateDefaultContextForAsset replacement?
](https://groups.google.com/g/usd-interest/c/7Aqv3k-V_DU/m/HPz7dSZLBQAJ)

Please consider contributing back to the Usd project in the  official [Usd Repository](https://github.com/PixarAnimationStudios/USD) and via the [Usd User groups](https://wiki.aswf.io/display/WGUSD/USD+Working+Group).

Feel free to fork this repository and share improvements or further resolvers.
If you run into issues, please flag them by [submitting a ticket](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new).
