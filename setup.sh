export PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/FileResolver/bin:/opt/hfs19.5/python/bin:$PATH
export PYTHONPATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/FileResolver/lib/python:/opt/hfs19.5/python/lib/python3.9/site-packages:$PYTHONPATH
export PXR_PLUGINPATH_NAME=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/FileResolver/resources:$PXR_PLUGINPATH_NAME
export LD_LIBRARY_PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/FileResolver/lib:$LD_LIBRARY_PATH

pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null