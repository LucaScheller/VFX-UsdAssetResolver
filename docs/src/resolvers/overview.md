# Overview
All resolvers share these common features:
- A simple mapping pair look up in a provided mapping pair Usd file. The mapping data has to stored in the Usd layer metadata in an key called ```mappingPairs``` as an array with the syntax ```["sourcePathA.usd", "targetPathA.usd", "sourcePathB.usd", "targetPathB.usd"]```. (This is quite similar to Rodeo's asset resolver that can be found [here](https://github.com/rodeofx/rdo_replace_resolver) using the AR 1.0 specification.)
- The search path environment variable by default is ```AR_SEARCH_PATHS```. It can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- You can use the ```AR_ENV_SEARCH_REGEX_EXPRESSION```/```AR_ENV_SEARCH_REGEX_FORMAT``` environment variables to preformat any asset paths before they looked up in the ```mappingPairs```. The regex match found by the ```AR_ENV_SEARCH_REGEX_EXPRESSION``` environment variable will be replaced by the content of the  ```AR_ENV_SEARCH_REGEX_FORMAT``` environment variable. The environment variable names can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same pinning file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the pinning file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)

# Resolvers
- [File Resolver](./FileResolver/overview.md)
- [Python Resolver](./PythonResolver/overview.md)

# Environment Variables

## USD Plugin Configuration
In order for our plugin to be found by USD, we have to specify a few environment variables.
Run this in your terminal before running your USD capable app. If your are using a pre-compiled release build, redirect the paths accordingly.
~~~admonish info title=""
```bash
# Linux
export RESOLVER_NAME=<InsertResolverName> # E.g. fileResolver
export PYTHONPATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib/python:${PYTHONPATH}
export PXR_PLUGINPATH_NAME=${REPO_ROOT}/dist/${RESOLVER_NAME}/resources:${PXR_PLUGINPATH_NAME}
export LD_LIBRARY_PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib
# Windows
set RESOLVER_NAME=<InsertResolverName> # E.g. fileResolver
set PYTHONPATH=%REPO_ROOT%/dist/%RESOLVER_NAME%/lib/python:%PYTHONPATH%
set PXR_PLUGINPATH_NAME=%REPO_ROOT%/dist/%RESOLVER_NAME%/resources:%PXR_PLUGINPATH_NAME%
set PATH=%REPO_ROOT%/dist/%RESOLVER_NAME%/lib:%PATH%
```
~~~

## Resolver Configuration

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
# Debugging

## Using the `TF_DEBUG` environment variable
To check what resolver has been loaded, you can set the `TF_DEBUG` env variable to `AR_RESOLVER_INIT`:
~~~admonish info title=""
```bash
export TF_DEBUG=AR_RESOLVER_INIT
```
~~~
For example this will yield the following when run with the Python Resolver:
~~~admonish info title=""
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
~~~
## Loading the Python Module
When importing the Python module, be sure to first import the Ar module, otherwise you might run into errors, as the resolver is not properly initialized:
~~~admonish info title=""
```bash
# Start python via the aliased `usdpython`
# Our sourced setup.sh aliases Houdini's standalone python to usdpython
# as well as sources extra libs like Usd
usdpython
```
~~~
~~~admonish info title=""
```python
# First import Ar, so that the resolver is initialized
from pxr import Ar
from usdAssetResolver import FileResolver
```
~~~