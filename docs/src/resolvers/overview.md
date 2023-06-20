# Overview
All resolvers share these common features:
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)

# Resolvers
- [File Resolver](./FileResolver/overview.md)
- [Python Resolver](./PythonResolver/overview.md)

# Debugging

## Using the `TF_DEBUG` environment variable
To check what resolver has been loaded, you can set the `TF_DEBUG` env variable to `AR_RESOLVER_INIT`:
```bash
export TF_DEBUG=AR_RESOLVER_INIT
```
For example this will yield the following when run with the Python Resolver:
```python
ArGetResolver(): Found primary asset resolver types: [PythonResolver, ArDefaultResolver]
ArGetResolver(): Using asset resolver PythonResolver from plugin ${REPO_ROOT}/dist/pythonResolver/lib/pythonResolver.so for primary resolver
ArGetResolver(): Found URI resolver ArDefaultResolver
ArGetResolver(): Found URI resolver FS_ArResolver
ArGetResolver(): Using FS_ArResolver for URI scheme(s) ["op", "opdef", "oplib", "opdatablock"]
ArGetResolver(): Found URI resolver PythonResolver
ArGetResolver(): Found package resolver USD_NcPackageResolver
ArGetResolver(): Using package resolver USD_NcPackageResolver for usdlc from plugin usdNc
ArGetResolver(): Using package resolver USD_NcPackageResolver for usdnc from plugin usdNc
ArGetResolver(): Found package resolver Usd_UsdzResolver
ArGetResolver(): Using package resolver Usd_UsdzResolver for usdz from plugin usd
```

## Loading the Python Module
When importing the Python module, be sure to first import the Ar module, otherwise you might run into errors, as the resolver is not properly initialized:
```bash
# Start python via the aliased `usdpython`
# Our sourced setup.sh aliases Houdini's standalone python to usdpython
# as well as sources extra libs like Usd
usdpython
```

```python
# First import Ar, so that the resolver is initialized
from pxr import Ar
from usdAssetResolver import FileResolver
```