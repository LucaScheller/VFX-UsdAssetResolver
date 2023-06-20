# Overview
All resolvers share these common features:
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)

# Resolvers
- [File Resolver](./FileResolver/overview.md)
- [Python Resolver](./PythonResolver/overview.md)