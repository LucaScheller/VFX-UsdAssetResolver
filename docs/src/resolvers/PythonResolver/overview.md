
# Python Resolver
## Overview
Python based implemention of the [file resolver](../FileResolver/overview.md):
{{#include ../shared_features.md:resolverSharedFeatures}}
- This resolver has feature parity to the file resolver, but the implementation is slightly different. The goal of this resolver is to enable easier RnD by running all resolver and resolver context related methods in Python. It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database related pipelines in Python.
- Running in Python does not allow proper multithreading due to Python's [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock), so this resolver should not be used in (large scale) productions. 

{{#include ../shared_features.md:resolverEnvConfiguration}}

## Debug Codes
Adding following tokens to the `TF_DEBUG` env variable will log resolver information about resolution/the context respectively.
* `PYTHONRESOLVER_RESOLVER`
* `PYTHONRESOLVERR_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=PYTHONRESOLVERR_RESOLVER_CONTEXT
```