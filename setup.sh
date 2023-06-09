export PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdResolverExample/bin:${PATH}
export PYTHONPATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdResolverExample/lib/python:/opt/hfs19.5/python/lib/python3.9/site-packages:$PYTHONPATH
export PXR_PLUGINPATH_NAME=/mnt/data/PROJECT/UsdAssetResolver/dist/usdResolverExample/resources
export LD_LIBRARY_PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdResolverExample/lib

pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null