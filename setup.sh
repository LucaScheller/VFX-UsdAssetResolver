# Source repo
if [ ! $REPO_SOURCED ]
then
    # Define repo root
    export REPO_SOURCED=1
    export REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && (pwd -W 2> /dev/null || pwd))
    # Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'cachedResolver'/'httpResolver'
    export AR_RESOLVER_NAME=cachedResolver
    export AR_RESOLVER_NAME_UPPERCASE=$(echo ${AR_RESOLVER_NAME} | tr '[:lower:]' '[:upper:]')
    # DCC
    export AR_DCC_NAME=HOUDINI
    if [ "$AR_DCC_NAME" == "HOUDINI" ]; then
        # Source Houdini (This defines what Houdini version to compile against)
        pushd /opt/hfs21.0 > /dev/null
        source houdini_setup
        popd > /dev/null
    fi
    if [ "$AR_DCC_NAME" == "MAYA" ]; then
        export MAYA_USD_SDK_ROOT="/path/to/maya/usd/sdk/root/.../mayausd/USD"
        export MAYA_USD_SDK_DEVKIT_ROOT="/path/to/maya/usd/sdk/root/.../content/of/devkit.zip"
        export PYTHON_ROOT="/path/to/python/root"
    fi
    # Source env
    export PYTHONPATH=${REPO_ROOT}/dist/${AR_RESOLVER_NAME}/lib/python:${PYTHONPATH}
    export PXR_PLUGINPATH_NAME=${REPO_ROOT}/dist/${AR_RESOLVER_NAME}/resources:${PXR_PLUGINPATH_NAME}
    export LD_LIBRARY_PATH=${REPO_ROOT}/dist/${AR_RESOLVER_NAME}/lib:${LD_LIBRARY_PATH}
    alias  usdpython="$HFS/python/bin/python $@"
    # Configure resolver
    export AR_SEARCH_PATHS=${REPO_ROOT}/files/generic
    export AR_SEARCH_REGEX_EXPRESSION="(bo)"
    export AR_SEARCH_REGEX_FORMAT="Bo"
    # Debug
    # export TF_DEBUG=${AR_RESOLVER_NAME_UPPERCASE}_RESOLVER
    export TF_DEBUG=AR_RESOLVER_INIT
    # Log
    echo "The resolver environment for resolver '${AR_RESOLVER_NAME}' has been initialized." 
fi


