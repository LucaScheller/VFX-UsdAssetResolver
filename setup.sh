# Source repo
export REPO_ROOT=${PROJECT}/UsdAssetResolver
export RESOLVER_NAME=pythonResolver
export RESOLVER_NAME_UPPERCASE=$(echo ${RESOLVER_NAME} | tr '[:lower:]' '[:upper:]')
# Source env
export PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/bin:${PATH}
export PYTHONPATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib/python:/opt/hfs19.5/python/lib/python3.9/site-packages:$PYTHONPATH
export PXR_PLUGINPATH_NAME=${REPO_ROOT}/dist/${RESOLVER_NAME}/resources
export LD_LIBRARY_PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib
# Source Houdini
pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null
export HOUDINI_LMINFO_VERBOSE=1
# Configure resolver
export AR_SEARCH_PATHS=${REPO_ROOT}/files
export AR_SEARCH_REGEX_EXPRESSION="(bo)"
export AR_ENV_SEARCH_REGEX_FORMAT="Bo"
# Debug
export TF_DEBUG=${RESOLVER_NAME_UPPERCASE}_RESOLVER_CONTEXT