## Overview
You can import the Python module as follows:
```python
from pxr import Ar
from usdAssetResolver import CachedResolver
```

## Tokens
Tokens can be found in CachedResolver.Tokens:
```python
CachedResolver.Tokens.mappingPairs
```

## Resolver
We optionally can also hook into relative path identifier creation via Python. 

This can be enabled by setting the `AR_CACHEDRESOLVER_ENV_EXPOSE_RELATIVE_PATH_IDENTIFIERS` environment variable to `1` or by calling `pxr.Ar.GetUnderlyingResolver().SetExposeRelativePathIdentifierState(True)`.

We then have access in our `PythonExpose.py` -> `Resolver.CreateRelativePathIdentifier` method. Here we can then return a non file path (anything that doesn't start with "/"/"./"/"../") identifier for our relative path, which then also gets passed to our `PythonExpose.py` -> `ResolverContext.ResolveAndCache` method.

This allows us to also redirect relative paths to our liking for example when implementing special pinning/mapping behaviours.

For more info check out our [production example](./example.md) section.

As with our mapping and caching pairs, the result is cached in C++ to enable faster lookups on consecutive calls.

As identifiers are context independent, the cache is stored on the resolver itself. See below on how to modify and inspect the cache.

```python
from pxr import Ar, Usd
from usdAssetResolver import CachedResolver

# Enable relative identifier modification
cached_resolver = Ar.GetUnderlyingResolver()
cached_resolver.SetExposeRelativePathIdentifierState(True)
print("Resolver is currently exposing relative path identifiers to Python | {}".format(cached_resolver.GetExposeRelativePathIdentifierState()))
# Or set the "AR_CACHEDRESOLVER_ENV_EXPOSE_RELATIVE_PATH_IDENTIFIERS" environment variable to 1.
# This can't be done via Python, as it has to happen before the resolver is loaded.
cached_resolver.GetExposeRelativePathIdentifierState() # Get the state of exposing relative path identifiers
cached_resolver.SetExposeRelativePathIdentifierState() # Set the state of exposing relative path identifiers

# We can also inspect and edit our relative identifiers via the following methods on the resolver.
# You'll usually only want to use these outside of the Resolver.CreateRelativePathIdentifier method only for debugging.
# The identifier cache is not context dependent (as identifiers are not).
cached_resolver.GetCachedRelativePathIdentifierPairs()       # Returns all cached relative path identifier pairs as a dict
cached_resolver.AddCachedRelativePathIdentifierPair()        # Add a cached relative path identifier pair
cached_resolver.RemoveCachedRelativePathIdentifierByKey()    # Remove a cached relative path identifier pair by key
cached_resolver.RemoveCachedRelativePathIdentifierByValue()  # Remove a cached relative path identifier pair by value
cached_resolver.ClearCachedRelativePathIdentifierPairs()     # Clear all cached relative path identifier pairs
```

## Resolver Context
You can manipulate the resolver context (the object that holds the configuration the resolver uses to resolve paths) via Python in the following ways:

```python
from pxr import Ar, Usd
from usdAssetResolver import CachedResolver

# Get via stage
stage = Usd.Stage.Open("/some/stage.usd")
context_collection = stage.GetPathResolverContext()
cachedResolver_context = context_collection.Get()[0]
# Or context creation
cachedResolver_context = CachedResolver.ResolverContext()

# To print a full list of exposed methods:
for attr in dir(CachedResolver.ResolverContext):
    print(attr)
```

### Refreshing the Resolver Context
```admonish important
If you make changes to the context at runtime, you'll need to refresh it!
```
You can reload it as follows, that way the active stage gets the change notification.

```python
from pxr import Ar
from usdAssetResolver import CachedResolver
resolver = Ar.GetResolver()
stage = pxr.Usd.Stage.Open("/some/stage.usd")
context_collection = stage.GetPathResolverContext()
cachedResolver_context = context_collection.Get()[0]
# Make edits as described below to the context.
cachedResolver_context.AddMappingPair("identifier.usd", "/absolute/file/path/destination.usd")
# Trigger Refresh (Some DCCs, like Houdini, additionally require node re-cooks.)
resolver.RefreshContext(context_collection)
```

### Editing the Resolver Context
We can edit the mapping and cache via the resolver context.
We also use these methods in the `PythonExpose.py` module.

```python
import json
stage = pxr.Usd.Stage.Open("/some/stage.usd")
context_collection = stage.GetPathResolverContext()
cachedResolver_context = context_collection.Get()[0]

# Mapping Pairs (Same as Caching Pairs, but have a higher loading priority)
cachedResolver_context.AddMappingPair("identifier.usd", "/absolute/file/path/destination.usd")
# Caching Pairs
cachedResolver_context.AddCachingPair("identifier.usd", "/absolute/file/path/destination.usd")
# Clear mapping and cached pairs (but not the mapping file path)
cachedResolver_context.ClearAndReinitialize()
# Load mapping from mapping file
cachedResolver_context.SetMappingFilePath("/some/mapping/file.usd")
cachedResolver_context.ClearAndReinitialize()

# Trigger Refresh (Some DCCs, like Houdini, additionally require node re-cooks.)
resolver.RefreshContext(context_collection)
```
When the context is initialized for the first time, it runs the `ResolverContext.Initialize` method as described below. Here you can add any mapping and/or cached pairs as you see fit.

### Mapping/Caching Pairs
To inspect/tweak the active mapping/caching pairs, you can use the following:
```python
ctx.ClearAndReinitialize()                    # Clear mapping and cache pairs and re-initialize context (with mapping file path)
ctx.GetMappingFilePath()                      # Get the mapping file path (Defaults to file that the context created via Resolver.CreateDefaultContextForAsset() opened")
ctx.SetMappingFilePath(p: str)                # Set the mapping file path
ctx.RefreshFromMappingFilePath()              # Reload mapping pairs from the mapping file path
ctx.GetMappingPairs()                         # Returns all mapping pairs as a dict
ctx.AddMappingPair(src: string, dst: str)     # Add a mapping pair
ctx.RemoveMappingByKey(src: str)              # Remove a mapping pair by key
ctx.RemoveMappingByValue(dst: str)            # Remove a mapping pair by value
ctx.ClearMappingPairs()                       # Clear all mapping pairs
ctx.GetCachingPairs()                         # Returns all caching pairs as a dict
ctx.AddCachingPair(src: string, dst: str)     # Add a caching pair
ctx.RemoveCachingByKey(src: str)              # Remove a caching pair by key
ctx.RemoveCachingByValue(dst: str)            # Remove a caching pair by value
ctx.ClearCachingPairs()                       # Clear all caching pairs
```

To generate a mapping .usd file, you can do the following:
```python
from pxr import Ar, Usd, Vt
from usdAssetResolver import CachedResolver
stage = Usd.Stage.CreateNew('/some/path/mappingPairs.usda')
mapping_pairs = {'assets/assetA/assetA.usd':'/absolute/project/assets/assetA/assetA_v005.usd', '/absolute/project/shots/shotA/shotA_v000.usd':'shots/shotA/shotA_v003.usd'}
mapping_array = []
for source_path, target_path in mapping_pairs.items():
    mapping_array.extend([source_path, target_path])
stage.SetMetadata('customLayerData', {CachedResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)})
stage.Save()
```

### PythonExpose.py Overview
As described in our [overview](./overview.md) section, the cache population is handled completely in Python, making it ideal for smaller studios, who don't have the C++ developer resources.

You can find the basic implementation version that gets shipped with the compiled code here:
[PythonExpose.py](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/src/CachedResolver/PythonExpose.py).

```admonish important
You can live edit it after the compilation here: ${REPO_ROOT}/dist/cachedResolver/lib/python/PythonExpose.py (or resolvers.zip/CachedResolver/lib/python folder if you are using the pre-compiled releases).
Since the code just looks for the `PythonExpose.py` file anywhere in the `sys.path` you can also move or re-create the file anywhere in the path to override the behaviour. The module name can be controlled by the `CMakeLists.txt` file in the repo root by setting `AR_CACHEDRESOLVER_USD_PYTHON_EXPOSE_MODULE_NAME` to a different name.

You'll want to adjust the content, so that identifiers get resolved and cached to what your pipeline needs.
```

```admonish tip
We also recommend checking out our unit tests of the resolver to see how to interact with it. You can find them in the "<Repo Root>/src/CachedResolver/testenv" folder or on [GitHub](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/src/CachedResolver/testenv/testCachedResolver.py).
```

Below we show the Python exposed methods, note that we use static methods, as we just call into the module and don't create the actual object. (This module could just as easily been made up of pure functions, we just create the classes here to make it match the C++ API.)

To enable a similar logging as the `TF_DEBUG` env var does, you can uncomment the following in the `log_function_args` function.

```python
...code...
def log_function_args(func):
    ...code...
    # To enable logging on all methods, re-enable this.
    # LOG.info(f"{func.__module__}.{func.__qualname__} ({func_args_str})")
...code...
```

#### Resolver

```python
class Resolver:

    @staticmethod
    @log_function_args
    def CreateRelativePathIdentifier(resolver, anchoredAssetPath, assetPath, anchorAssetPath):
        """Returns an identifier for the asset specified by assetPath.
        It is very important that the anchoredAssetPath is used as the cache key, as this
        is what is used in C++ to do the cache lookup.

        We have two options how to return relative identifiers:
        - Make it absolute: Simply return the anchoredAssetPath. This means the relative identifier
                            will not be passed through to ResolverContext.ResolveAndCache.
        - Make it non file based: Make sure the remapped identifier does not start with "/", "./" or"../"
                                  by putting some sort of prefix in front of it. The path will then be
                                  passed through to ResolverContext.ResolveAndCache, where you need to re-construct
                                  it to an absolute path of your liking. Make sure you don't use a "<somePrefix>:" syntax,
                                  to avoid mixups with URI based resolvers.

        Args:
            resolver (CachedResolver): The resolver
            anchoredAssetPath (str): The anchored asset path, this has to be used as the cached key.
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): A resolved anchor path.

        Returns:
            str: The identifier.
        """
        remappedRelativePathIdentifier = f"relativePath|{assetPath}?{anchorAssetPath}"
        resolver.AddCachedRelativePathIdentifierPair(anchoredAssetPath, remappedRelativePathIdentifier)
        return remappedRelativePathIdentifier
```

#### Resolver Context

```python
class ResolverContext:
    @staticmethod
    def Initialize(context):
        """Initialize the context. This get's called on default and post mapping file path
        context creation.

        Here you can inject data by batch calling context.AddCachingPair(assetPath, resolvePath),
        this will then populate the internal C++ resolve cache and all resolves calls
        to those assetPaths will not invoke Python and instead use the cache.

        Args:
            context (CachedResolverContext): The active context.
        """
        # Very important: In order to add a path to the cache, you have to call:
        #    context.AddCachingPair(assetPath, resolvedAssetPath)
        # You can add as many identifier->/abs/path/file.usd pairs as you want.
        context.AddCachingPair("identifier", "/some/path/to/a/file.usd")

    @staticmethod
    def ResolveAndCache(context, assetPath):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            context (CachedResolverContext): The active context.
            assetPath (str): An unresolved asset path.
        Returns:
            str: The resolved path string. If it points to a non-existent file,
                 it will be resolved to an empty ArResolvedPath internally, but will
                 still count as a cache hit and be stored inside the cachedPairs dict.
        """
        # Very important: In order to add a path to the cache, you have to call:
        #    context.AddCachingPair(assetPath, resolvedAssetPath)
        # You can add as many identifier->/abs/path/file.usd pairs as you want.
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        return resolved_asset_path
```