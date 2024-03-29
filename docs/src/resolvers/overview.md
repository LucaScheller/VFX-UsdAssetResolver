# Resolvers
Asset resolvers that can be compiled via this repository:
{{#include ./shared_features.md:resolverOverview}}

## USD Plugin Configuration
In order for our plugin to be found by USD, we have to specify a few environment variables.
Run this in your terminal before running your USD capable app. If your are using a pre-compiled release build, redirect the paths accordingly.

~~~admonish tip
If you are using our quick install method, this will already have been done for you via the "launch.sh/.bat" file in the directory where you downloaded the compiled release to. See our [Automatic Installation](../installation/automatic_install.md) section for more information.
~~~

~~~admonish info title=""
```bash
# Linux
export PYTHONPATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib/python:${PYTHONPATH}
export PXR_PLUGINPATH_NAME=${REPO_ROOT}/dist/${RESOLVER_NAME}/resources:${PXR_PLUGINPATH_NAME}
export LD_LIBRARY_PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib
export TF_DEBUG=AR_RESOLVER_INIT # Debug Logs
# Windows
set PYTHONPATH=%REPO_ROOT%\dist\%RESOLVER_NAME%\lib\python;%PYTHONPATH%
set PXR_PLUGINPATH_NAME=%REPO_ROOT%\dist\%RESOLVER_NAME%\resources;%PXR_PLUGINPATH_NAME%
set PATH=%REPO_ROOT%\dist\%RESOLVER_NAME%\lib;%PATH%
set TF_DEBUG=AR_RESOLVER_INIT # Debug Logs
```
~~~

If it loads correctly, you'll see something like this in the terminal output:
~~~admonish info title=""
```bash
ArGetResolver(): Found primary asset resolver types: [FileResolver, ArDefaultResolver]
```
~~~

## Debugging
### By using the `TF_DEBUG` environment variable
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

### By loading the Python Module
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