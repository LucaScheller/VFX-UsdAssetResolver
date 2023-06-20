# Example Usd files and mapping pair files
To explain the above resolver setups, we assume the following scene setup:
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
Content of the USD file located at `/workspace/shots/shotA/shotA_mapping.usd`

```python
#usda 1.0
(
    customLayerData = {
        string[] mappingPairs = ["testAssetA/testAssetA.usda", "testAssetA/testAssetA_v001.usda"]
    }


```

Content of the USD files located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v002.usd`
```python
#usda 1.0
def Cube "box" ()
{
    double size = 2
}
```
Content of the USD file located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v001.usd`
```python
#usda 1.0
def Cylinder "box" ()
{
}
```