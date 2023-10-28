#// ANCHOR: resolverOverview
- **Production Resolvers**
    - **File Resolver** - A file system based resolver similar to the default resolver with support for custom mapping pairs as well as at runtime modification and refreshing.
    - **Cached Resolver** - Still work in progress, more info coming soon.
- **RnD Resolvers**
    - **Python Resolver** - Python based implementation of the file resolver. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database interactions in Python for initial research.
- **Proof Of Concept Resolvers**
    - **Http Resolver** - A proof of concept http resolver. This is kindly provided and maintained by @charlesfleche in the [arHttp: Offloads USD asset resolution to an HTTP server
    ](https://github.com/charlesfleche/arHttp) repository. For documentation, feature suggestions and bug reports, please file a ticket there. This repo handles the auto-compilation against DCCs and exposing to the automatic installation update manager UI.
#// ANCHOR_END: resolverOverview

#// ANCHOR: resolverSharedFeatures
- A simple mapping pair look up in a provided mapping pair Usd file. The mapping data has to stored in the Usd layer metadata in an key called ```mappingPairs``` as an array with the syntax ```["sourcePathA.usd", "targetPathA.usd", "sourcePathB.usd", "targetPathB.usd"]```. (This is quite similar to Rodeo's asset resolver that can be found [here](https://github.com/rodeofx/rdo_replace_resolver) using the AR 1.0 specification.)
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- You can use the ```AR_ENV_SEARCH_REGEX_EXPRESSION```/```AR_ENV_SEARCH_REGEX_FORMAT``` environment variables to preformat any asset paths before they looked up in the ```mappingPairs```. The regex match found by the ```AR_ENV_SEARCH_REGEX_EXPRESSION``` environment variable will be replaced by the content of the  ```AR_ENV_SEARCH_REGEX_FORMAT``` environment variable. The environment variable names can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)
#// ANCHOR_END: resolverSharedFeatures

#// ANCHOR: resolverEnvConfiguration
## Resolver Environment Configuration
- `AR_SEARCH_PATHS`: The search path for non absolute asset paths.
- `AR_SEARCH_REGEX_EXPRESSION`: The regex to preformat asset paths before mapping them via the mapping pairs.
- `AR_SEARCH_REGEX_FORMAT`: The string to replace with what was found by the regex expression.

The resolver uses these env vars to resolve non absolute asset paths relative to the directories specified by `AR_SEARCH_PATHS`. For example the following substitutes any occurrence of `v<3digits>` with `v000` and then looks up that asset path in the mapping pairs.

~~~admonish info title=""
```bash
export AR_SEARCH_PATHS="/workspace/shots:/workspace/assets"
export AR_SEARCH_REGEX_EXPRESSION="(v\d\d\d)"
export AR_SEARCH_REGEX_FORMAT="v000"
```
~~~
#// ANCHOR_END: resolverEnvConfiguration