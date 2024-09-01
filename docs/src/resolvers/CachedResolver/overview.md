# Cached Resolver
## Overview
```admonish tip
This resolver first consults an internal resolver context dependent cache to resolve asset paths. If the asset path is not found in the cache, it will redirect the request to Python and cache the result. This is ideal for smaller studios, as this preserves the speed of C++ with the flexibility of Python.
```

By default (similar to the FileResolver and USD's default resolver), any absolute and relative file path is resolved as an on-disk file path. That means "normal" USD files, that don't use custom identifiers, will resolve as expected (and as fast as usual as this is called in C++).

```admonish tip title="Pro Tip"
Optionally you can opt-in into also exposing relative identifiers to Python by setting the `AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeRelativePathIdentifierState(True)`. This is a more advanced feature and is therefore disabled by default. See our [production example](example.md) section for more information on how to use this and why it can be useful.
```

All non file path identifiers (anything that doesn't start with "/", "./", "../") will forward their request to the `PythonExpose.py` -> `ResolverContext.ResolveAndCache` method.
If you want to customize this resolver, just edit the methods in PythonExpose.py to fit your needs. You can either edit the file directly or move it anywhere where your "PYTHONPATH"/"sys.path" paths look for Python modules.

```admonish tip title="Pro Tip"
Optionally you can opt-in into also exposing absolute identifiers (so all (absolute/relative/identifiers that don't start with "/","./","../") identifiers) to Python by setting the `AR_EXPOSE_ABSOLUTE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeAbsolutePathIdentifierState(True)`. This enforces all identifiers to run through Python. Use this with care, we recommend only using this for debugging or when having a large dataset of pre-cached mapping pairs easily available.
```

We also recommend checking out our unit tests of the resolver to see how to interact with it. You can find them in the "<Repo Root>/src/CachedResolver/testenv" folder or on [GitHub](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/src/CachedResolver/testenv/testCachedResolver.py).

Here is a full list of features:
- We support adding caching pairs in two ways, cache-lookup-wise they do the same thing, except the "MappingPairs" have a higher priority than "CachedPairs":
    - **MappingPairs**: All resolver context methods that have `Mapping` in their name, modify the internal `mappingPairs` dictionary. As with the [FileResolver](../FileResolver/overview.md) and [PythonResolver](../PythonResolver/overview.md) resolvers, mapping pairs get populated when creating a new context with a specified mapping file or when editing it via the exposed Python resolver context methods. When loading from a file, the mapping data has to be stored in the Usd layer metadata in an key called ```mappingPairs``` as an array with the syntax ```["sourceIdentifierA.usd", "/absolute/targetPathA.usd", "sourceIdentifierB.usd", "/absolute/targetPathB.usd"]```. (This is quite similar to Rodeo's asset resolver that can be found [here](https://github.com/rodeofx/rdo_replace_resolver) using the AR 1.0 specification.). See our [Python API](./PythonAPI.md) page for more information.
    - **CachingPairs**: All resolver context methods that have `Caching` in their name, modify the internal `cachingPairs` dictionary. With this dictionary it is up to you when to populate it. In our `PythonExpose.py` file, we offer two ways where you can hook into the resolve process. In both of them you can add as many cached lookups as you want via `ctx.AddCachingPair(asset_path, resolved_asset_path)`:
        - On context creation via the `PythonExpose.py` -> `ResolverContext.Initialize` method. This gets called whenever a context gets created (including the fallback default context). For example Houdini creates the default context if you didn't specify a "Resolver Context Asset Path" in your stage on the active node/in the stage network. If you do specify one, then a new context gets spawned that does the above mentioned mapping pair lookup and then runs the `PythonExpose.py` -> `ResolverContext.Initialize` method.
        - On resolve for non file path identifiers (anything that doesn't start with "/"/"./"/"../") via the `PythonExpose.py` -> `ResolverContext.ResolveAndCache` method. Here you are free to only add the active asset path via `ctx.AddCachingPair(asset_path, resolved_asset_path)` or any number of relevant asset paths.
- We optionally also support hooking into relative path identifier creation via Python. This can be enabled by setting the `AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeRelativePathIdentifierState(True)`. We then have access in our `PythonExpose.py` -> `Resolver.CreateRelativePathIdentifier` method. Here we can then return a non file path (anything that doesn't start with "/"/"./"/"../") identifier for our relative path, which then also gets passed to our `PythonExpose.py` -> `ResolverContext.ResolveAndCache` method. This allows us to also redirect relative paths to our liking for example when implementing special pinning/mapping behaviours. For more info check out our [production example](./example.md) section. As with our mapping and caching pairs, the result is cached in C++ to enable faster lookups on consecutive calls. As identifiers are context independent, the cache is stored on the resolver itself. See our [Python API](./PythonAPI.md) section on how to clear the cache.
- We optionally also support exposing alle path identifiers to our `ResolverContext.ResolveAndCache` Python method. This can be enabled by setting the `AR_EXPOSE_ABSOLUTE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeAbsolutePathIdentifierState(True)`. This then forwards any path to be run through our Python exposed method, regardless of how the identifier is formatted. Use this with care, we recommend only using this for debugging or when having a large dataset of pre-cached mapping pairs easily available.
- In comparison to our [FileResolver](../FileResolver/overview.md) and [PythonResolver](../PythonResolver/overview.md), the mapping/caching pair values need to point to the absolute disk path (instead of using a search path). We chose to make this behavior different, because in the "PythonExpose.py" you can directly customize the "final" on-disk path to your liking.  
- The resolver contexts are cached globally, so that DCCs, that try to spawn a new context based on the same mapping file using the [```Resolver.CreateDefaultContextForAsset```](https://openusd.org/dev/api/class_ar_resolver.html), will re-use the same cached resolver context. The resolver context cache key is currently the mapping file path. This may be subject to change, as a hash might be a good alternative, as it could also cover non file based edits via the exposed Python resolver API.
- ```Resolver.CreateContextFromString```/```Resolver.CreateContextFromStrings``` is not implemented due to many DCCs not making use of it yet. As we expose the ability to edit the context at runtime, this is also often not necessary. If needed please create a request by submitting an issue here: [Create New Issue](https://github.com/LucaScheller/VFX-UsdAssetResolver/issues/new)
- Refreshing the stage is also supported, although it might be required to trigger additional reloads in certain DCCs.


```admonish warning
While the resolver works and gives us the benefits of Python and C++, we don't guarantee its scalability. If you look into our source code, you'll also see that our Python invoke call actually circumvents the "const" constant variable/pointers in our C++ code. USD API-wise the resolve ._Resolve calls should only access a read-only context. We side-step this design by modifying the context in Python. Be aware that this could have side effects.
```

## Debug Codes
Adding following tokens to the `TF_DEBUG` env variable will log resolver information about resolution/the context respectively.
* `CACHEDRESOLVER_RESOLVER`
* `CACHEDRESOLVER_RESOLVER_CONTEXT`

For example to enable it on Linux run the following before executing your program:

```bash
export TF_DEBUG=CACHEDRESOLVER_RESOLVER_CONTEXT
```