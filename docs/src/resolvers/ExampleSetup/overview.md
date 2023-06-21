# Example Usd files and mapping pair files
An example scene setup might looks as follows:
- The following files on disk:
    - `/workspace/shots/shotA/shotA.usd`
    - `/workspace/shots/shotA/shotA_mapping.usd`
    - `/workspace/assets/assetA/assetA.usd`
    - `/workspace/assets/assetA/assetA_v001.usd`
    - `/workspace/assets/assetA/assetA_v002.usd`
- The ```AR_SEARCH_PATHS``` environment variable being set to `/workspace/shots:/workspace/assets`

In the <REPO_ROOT>/files folder you can find this setup. To run it, you must set the `AR_SEARCH_PATHS` env var as follows.
```bash
export AR_SEARCH_PATHS=${REPO_ROOT}/files/workspace/shots:${REPO_ROOT}/files/workspace/assets
```
And then open up the `shots/shotA/shotA.usd` file and set the resolver context mapping file path to `shots/shotA/shotA_mapping.usd`. 

In Houdini this is done by loading the shot file via a sublayer node and setting the `Resolver Context Asset Path` parm to the mapping file path in the [`Scene Graph Tree`>`Opens the parameter dialog for the current LOP Network`](https://www.sidefx.com/docs/houdini/ref/panes/scenegraphtree.html) button.

# Content structure

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
)
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