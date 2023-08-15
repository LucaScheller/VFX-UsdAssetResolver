# Source repo
if [ ! $REPO_SOURCED ]
then
    # Define repo root
    export REPO_SOURCED=1
    export REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && (pwd -W 2> /dev/null || pwd))
    # Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'hybridResolver'
    export RESOLVER_NAME=fileResolver
    export RESOLVER_NAME_UPPERCASE=$(echo ${RESOLVER_NAME} | tr '[:lower:]' '[:upper:]')
    # Source Houdini (This defines what Houdini version to compile against)
    pushd /opt/hfs19.5 > /dev/null
    source houdini_setup
    popd > /dev/null
    export HOUDINI_LMINFO_VERBOSE=1
    # Source env
    export HOU_PYTHON_VERSION="$(cut -d ' ' -f 2 <<< `hython --version`)"
    export HOU_PYTHON_SHORTVERSION=${HOU_PYTHON_VERSION%.*}
    export PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/bin:${PATH}
    export PYTHONPATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib/python:${HFS}/python/lib/python${HOU_PYTHON_SHORTVERSION}/site-packages:$PYTHONPATH
    export PXR_PLUGINPATH_NAME=${REPO_ROOT}/dist/${RESOLVER_NAME}/resources:${PXR_PLUGINPATH_NAME}
    export LD_LIBRARY_PATH=${REPO_ROOT}/dist/${RESOLVER_NAME}/lib:${HFS}/python/lib:${HFS}/dsolib
    alias  usdpython="$HFS/python/bin/python $@"
    # Configure resolver
    export AR_SEARCH_PATHS=${REPO_ROOT}/files
    export AR_SEARCH_REGEX_EXPRESSION="(bo)"
    export AR_SEARCH_REGEX_FORMAT="Bo"
    # Debug
    export TF_DEBUG=${RESOLVER_NAME_UPPERCASE}_RESOLVER
fi


