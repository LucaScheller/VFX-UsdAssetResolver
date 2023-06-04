export PYTHONPATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/lib/python:$PYTHONPATH
export PXR_PLUGINPATH_NAME=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/resources:$PXR_PLUGINPATH_NAME
export LD_LIBRARY_PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/usdSurvivalGuide/lib:$LD_LIBRARY_PATH

pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null