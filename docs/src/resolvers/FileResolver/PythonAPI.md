# Python API
## Overview
You can important the Python module as follows:
```python
from pxr import Ar, Vt
from usdAssetResolver import FileResolver
```


## Tokens
Tokens can be found in FileResolver.Tokens, for example:
```python
FileResolver.Tokens.mappingPairs
```
## Resolver Context
You can manipulate the resolver context (the object that holds the configuration the resolver uses to resolve paths) via Python in the following ways:

```python
stage = pxr.Usd.Stage.Open("/some/stage.usd")
ctx_collection = pxr.Usd.Stage.GetPathResolverContext()
ctx = ctx_collection[0]

# To print a full list of exposed methods:
for attr in dir(FileResolver.ResolverContext):
    print(attr)
```

### Refreshing the Resolver Context
```admonish important
If you make changes to the context at runtime, you'll need to refresh it!
```
You can reload it as follows, that way the active stage gets the change notification.

```python
resolver = Ar.GetResolver()
ctx_collection = stage.GetPathResolverContext()
ctx = ctx_collection[0]
# Make edits as described below to the context.
ctx.AddMappingPair("source.usd", "destination.usd")
# Trigger Refresh (Some DCCs, like Houdini, additionally require node re-cooks.)
stage.RefreshContext(ctx_collection)
```

### Search Paths
The search paths get read from the `AR_SEARCH_PATHS` env var by default. You can inspect and tweak the search paths at runtime by using the following methods:
```python
ctx.GetSearchPaths()                        # Returns all search paths (env and custom). 
ctx.RefreshSearchPaths()                    # Reloads env search paths and re-populates the search paths that the resolver uses. This must be called after changing the env var value or the custom search paths. 
ctx.GetEnvSearchPaths()                     # Returns all env search paths 
ctx.GetCustomSearchPaths()                  # Returns all custom search paths 
ctx.SetCustomSearchPaths(searchPaths: list) # Set custom search paths 
```

### Mapping Pairs
To inspect/tweak the active mapping pairs, you can use the following:
```python
ctx.GetMappingFilePath()                      # Get the mapping file path (Defaults file that the context created Resolver.CreateDefaultContextForAsset() opened)
ctx.SetMappingFilePath()                      # Set the mapping file path
ctx.RefreshFromMappingFilePath(filePath: str) # Reload mapping pairs from the mapping file path
ctx.GetMappingPairs()                         # Returns all mapping pairs as a dict
ctx.AddMappingPair(src: string, dst: str)     # Add a mapping pair
ctx.ClearMappingPairs()                       # Clear all mapping pairs
ctx.RemoveMappingByKey(src: str)              # Remove a mapping pair by key
ctx.RemoveMappingByValue(dst: str)            # Remove a mapping pair by value
```
To generate a mapping .usd file, you can do the following:
```python
stage = Usd.Stage.Open('/some/path/mappingPairs.usda')
mapping_pairs = {'assets/assetA/assetA.usd':'assets/assetA/assetA_v005.usd', 'shots/shotA/shotA_v000.usd':'shots/shotA/shotA_v003.usd'}
mapping_array = []
for source_path, target_path in mapping_pairs:
    mapping_array.extend([source_path, target_path])
stage.SetMetadata('customLayerData', {FileResolver.Tokens.mappingPairs: Vt.StringArray(mapping_array)})
stage.Save()
```

To change the asset path formatting before it is looked up in the mapping pairs, you can do the following:

```python
ctx.GetMappingRegexExpression()               # Get the regex expression
ctx.SetMappingRegexExpression(regex_str: str) # Set the regex expression
ctx.GetMappingRegexFormat()                   # Get the regex expression match formatting
ctx.SetMappingRegexFormat()                   # Set the regex expression match formatting
```