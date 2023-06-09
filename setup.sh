export PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/fileResolver/bin:${PATH}
export PYTHONPATH=/mnt/data/PROJECT/UsdAssetResolver/dist/fileResolver/lib/python:/opt/hfs19.5/python/lib/python3.9/site-packages:$PYTHONPATH
export PXR_PLUGINPATH_NAME=/mnt/data/PROJECT/UsdAssetResolver/dist/fileResolver/resources
export LD_LIBRARY_PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/fileResolver/lib

pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null