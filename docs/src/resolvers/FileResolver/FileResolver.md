
# Resolvers
## File Resolver
```python
# Python script executed from `/workspace/shots`
from pxr import Ar
from pxr import Usd
from pxr import Vt
from rdo import ReplaceResolver
from shutil import copyfile
from usdAssetResolver import FileResolver

import os

copyfile('published/shots/a_v1.usda', 'published/shots/a_v2.usda')

stage = Usd.Stage.Open('published/shots/a_v2.usda')
replaceFoo = ['assets/foo/v1/foo.usda', 'assets/foo/v2/foo.usda']
replacerBar = ['assets/bar/v4/bar.usda', 'assets/bar/v5/bar.usda']
mappingPairs = Vt.StringArray(replaceFoo + replacerBar)

# Add the replace data to the stage custom meta data
stage.SetMetadata('customLayerData', {FileResolver.Tokens.mappingPairs: mappingPairs})
stage.Save()

# Setup our anchor search path using the environmnet variable
os.environ['AR_SEARCH_PATHS'] = os.path.abspath('published')

# Open the new shot version and check the version attributes
stage = Usd.Stage.Open('published/shots/a_v2.usda')
assert (stage.GetPrimAtPath('/foo_01').GetAttribute('version').Get() == "v2")
assert (stage.GetPrimAtPath('/bar_01').GetAttribute('version').Get() == "v5")
```

## Debug Codes

Adding following tokens to *TF_DEBUG* will log resolver information about resolution/the context respectively.
* FILERESOLVER_RESOLVER
* FILERESOLVER_RESOLVER_CONTEXT

For example to enable it on Linux run the following before executing your program:

```export TF_DEBUG=FILERESOLVER_RESOLVER_CONTEXT```
# Example stage and mapping pair files
To explain the above resolver functionality, we assume the following setup:
- The following files on disk:
    - `/workspace/shots/shotA/shotA.usd`
    - `/workspace/shots/shotA/shotA_mapping.usd`
    - `/workspace/assets/assetA/assetA.usd`
    - `/workspace/assets/assetA/assetA_v001.usd`
    - `/workspace/assets/assetA/assetA_v002.usd`
- The ```AR_SEARCH_PATHS``` environment variable being set to `/workspace/assets`

Content of a USD file located at `/workspace/shots/shotA/shotA.usd`
```python
#usda 1.0

def "testAssetA" (
	prepend references = @assets/testAssetA/testAssetA.usda@
)
{
}
```
Content of the USD file located at `/workspace/shots/shotA/shotA.usd`

```python
#usda 1.0
(
    customLayerData = {
        string[] mappingPairs = ["testAssetA/testAssetA.usda", "testAssetA/testAssetA_v001.usda"]
    }


```

Content of the USD files located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v002.usd`
```python
def Cube "box" ()
{
    double size = 2
}
```
Content of the USD file located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v001.usd`
```python
def Cylinder "box" ()
{
}
```