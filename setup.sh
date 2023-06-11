# Source env
export PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/pythonResolver/bin:${PATH}
export PYTHONPATH=/mnt/data/PROJECT/UsdAssetResolver/dist/pythonResolver/lib/python:/opt/hfs19.5/python/lib/python3.9/site-packages:$PYTHONPATH
export PXR_PLUGINPATH_NAME=/mnt/data/PROJECT/UsdAssetResolver/dist/pythonResolver/resources
export LD_LIBRARY_PATH=/mnt/data/PROJECT/UsdAssetResolver/dist/pythonResolver/lib

# Source Houdini
pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null

# Configure resolver
export AR_SEARCH_PATHS=/mnt/data/PROJECT/UsdAssetResolver/files
export AR_SEARCH_REGEX_EXPRESSION="(bo)"
export AR_ENV_SEARCH_REGEX_FORMAT="Bo"
# Debug
export TF_DEBUG=FILERESOLVER_RESOLVER_CONTEXT