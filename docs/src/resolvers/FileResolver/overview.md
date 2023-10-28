# File Resolver
## Overview
This resolver is a file system based resolver similar to the default resolver with support for custom mapping pairs.
{{#include ../shared_features.md:resolverSharedFeatures}}
- You can adjust the resolver context content during runtime via exposed Python methods (More info [here](./PythonAPI.md)). Refreshing the stage is also supported, although it might be required to trigger additional reloads in certain DCCs.

{{#include ../shared_features.md:resolverEnvConfiguration}}

## Debug Codes
Adding following tokens to the `TF_DEBUG` env variable will log resolver information about resolution/the context respectively.
* `FILERESOLVER_RESOLVER`
* `FILERESOLVER_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=FILERESOLVER_RESOLVER_CONTEXT
```