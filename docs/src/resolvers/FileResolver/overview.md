# File Resolver
## Overview
A file system based resolver similar to the default resolver with support for custom mapping pairs.
- A simple mapping pair look up in a provided mapping pair Usd file. The mapping data has to stored in the Usd layer metadata in an key called ```mappingPairs``` as an array with the syntax ```["sourcePathA.usd", "targetPathA.usd", "sourcePathB.usd", "targetPathB.usd"]```. (This is quite similar to Rodeo's asset resolver that can be found [here](https://github.com/rodeofx/rdo_replace_resolver) using the AR 1.0 specification.)
- You can use the ```AR_ENV_SEARCH_REGEX_EXPRESSION```/```AR_ENV_SEARCH_REGEX_FORMAT``` environment variables to preformat any asset paths before they looked up in the ```mappingPairs```. The regex match found by the ```AR_ENV_SEARCH_REGEX_EXPRESSION``` environment variable will be replaced by the content of the  ```AR_ENV_SEARCH_REGEX_FORMAT``` environment variable. The environment variable names can be customized in the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) file.
- You can adjust the resolver context content during runtime via exposed Python methods (More info below). Refreshing the stage is also supported, although it might be required to trigger additional reloads in certain DCCs.

## Debug Codes
Adding following tokens to the *TF_DEBUG* env variable will log resolver information about resolution/the context respectively.
* `FILERESOLVER_RESOLVER`
* `FILERESOLVER_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=FILERESOLVER_RESOLVER_CONTEXT
```

## Environment Variables

- `AR_SEARCH_PATHS`: The search path for non absolute asset paths.
- `AR_SEARCH_REGEX_EXPRESSION`: The regex to preformat asset paths before mapping them via the mapping pairs.
- `AR_SEARCH_REGEX_FORMAT`: The string to replace with what was found by the regex expression.

The resolver uses these env vars to resolve non absolute asset paths relative to the directories specified by `AR_SEARCH_PATHS`. For example the following substitutes any occurrence of `v<3digits>` with `v000` and then looks up that asset path in the mapping pairs.

```bash
export AR_SEARCH_PATHS="/workspace/shots:/workspace/assets"
export AR_SEARCH_REGEX_EXPRESSION="(v\d\d\d)"
export AR_SEARCH_REGEX_FORMAT="v000"
```