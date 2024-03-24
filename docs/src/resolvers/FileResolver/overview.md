# File Resolver
## Overview
This resolver is a file system based resolver similar to the default resolver with support for custom mapping pairs.
{{#include ../shared_features.md:resolverSharedFeatures}}
- You can adjust the resolver context content during runtime via exposed Python methods (More info [here](./PythonAPI.md)). Refreshing the stage is also supported, although it might be required to trigger additional reloads in certain DCCs.
- We optionally also support exposing alle path identifiers to our `ResolverContext.ResolveAndCache` Python method. This can be enabled by setting the `AR_CACHEDRESOLVER_ENV_EXPOSE_ABSOLUTE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeAbsolutePathIdentifierState(True)`. This then forwards any path to be run through our mapped pairs mapping, regardless of how the identifier is formatted. 

```admonish tip title="Pro Tip"
Optionally you can opt-in into also exposing absolute identifiers (so all (absolute/relative/identifiers that don't start with "/","./","../") identifiers) to our mapping pair mechanism by setting the `AR_FILERESOLVER_ENV_EXPOSE_ABSOLUTE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeAbsolutePathIdentifierState(True)`. This enforces all identifiers to run through our mapped pairs mapping. The mapped result can also be a search path based path, which then uses the search paths to resolve itself. (So mapping from an absolute to search path based path via the mapping pairs is possible.)
```

{{#include ../shared_features.md:resolverEnvConfiguration}}


## Debug Codes
Adding following tokens to the `TF_DEBUG` env variable will log resolver information about resolution/the context respectively.
* `FILERESOLVER_RESOLVER`
* `FILERESOLVER_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=FILERESOLVER_RESOLVER_CONTEXT
```