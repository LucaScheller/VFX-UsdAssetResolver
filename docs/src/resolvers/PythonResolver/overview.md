
# Python Resolver
## Overview

Python based implemention of the file resolver:
- It implements the features listed in the [resolvers overview section](../overview.md).
- This resolver has feature parity to the file resolver, but the implementation is slightly different. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database related pipelines in Python.
- Running in Python does not allow proper multithreading due to Python's [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock), so this resolver should not be used in (large scale) productions. 


## Debug Codes
Adding following tokens to the `TF_DEBUG` env variable will log resolver information about resolution/the context respectively.
* `PYTHONRESOLVER_RESOLVER`
* `PYTHONRESOLVERR_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=PYTHONRESOLVERR_RESOLVER_CONTEXT
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