# Example Usd files and mapping pair files

```admonish warning
These examples currently work with the [File Resolver](../FileResolver/overview.md) and [Python Resolver](../PythonResolver/overview.md).

For resolver specific examples, see the corresponding resolver section.
```

## Simple Example

A very simple setup can be found in In the <REPO_ROOT>/files folder. 

Before launching a Usd related software, you'll have to set these env vars:
```bash
export AR_SEARCH_PATHS=${REPO_ROOT}/files/generic
export AR_SEARCH_REGEX_EXPRESSION="(bo)"
export AR_SEARCH_REGEX_FORMAT="Bo"
```
The `source setup.sh` bash script in the root of this repo also does this for your automatically.
After that load the `box.usda` in the application of your choice. Make sure to load `box.usda`and not `/path/to/repo/box.usda` as the resolver only resolves paths that use the search path mechanism.
You should now see a cube. If you set the resolver context to the `mapping.usda` file, it will be replaced to a cylinder.

## Production Example

A larger example scene setup might looks as follows:
- The following files on disk:
    - `/workspace/shots/shotA/shotA.usd`
    - `/workspace/shots/shotA/shotA_mapping.usd`
    - `/workspace/assets/assetA/assetA.usd`
    - `/workspace/assets/assetA/assetA_v001.usd`
    - `/workspace/assets/assetA/assetA_v002.usd`
- The ```AR_SEARCH_PATHS``` environment variable being set to `/workspace/shots:/workspace/assets`

In the <REPO_ROOT>/files folder you can also find this setup. To run it, you must set the `AR_SEARCH_PATHS` env var as follows.
```bash
export AR_SEARCH_PATHS=${REPO_ROOT}/files/generic/workspace/shots:${REPO_ROOT}/files/generic/workspace/assets
```
And then open up the `shots/shotA/shotA.usd` file and set the resolver context mapping file path to `shots/shotA/shotA_mapping.usd`. 

In Houdini this is done by loading the shot file via a sublayer node and setting the `Resolver Context Asset Path` parm to the mapping file path in the [`Scene Graph Tree`>`Opens the parameter dialog for the current LOP Network`](https://www.sidefx.com/docs/houdini/ref/panes/scenegraphtree.html) button.

You'll see the box being replaced to cylinder.

### Content structure

Content of a USD file located at `/workspace/shots/shotA/shotA.usd`
```python
#usda 1.0
def "testAssetA" (
    prepend references = @assetA/assetA.usd@</asset>
)
{
}
```
Content of the USD file located at `/workspace/shots/shotA/shotA_mapping.usd`

```python
#usda 1.0
(
    customLayerData = {
        string[] mappingPairs = ["assetA/assetA.usd", "assetA/assetA_v002.usd"]
    }
)
```

Content of the USD files located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v001.usd`
```python
#usda 1.0
def Cube "asset" ()
{
    double size = 2
}
```
Content of the USD file located at `/workspace/assets/assetA/assetA.usd` and `/workspace/assets/assetA/assetA_v002.usd`
```python
#usda 1.0
def Cylinder "asset" ()
{
}
```