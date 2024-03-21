repo_root=$(cd .; pwd)
export MAYA_USD_SDK_ROOT=$repo_root/dependency/install/maya_usd_sdk
export MAYA_USD_SDK_DEVKIT_ROOT=$repo_root/dependency/install/maya_usd_sdk_devkit
export PYTHON_ROOT=$repo_root/dependency/install/python
export AR_DCC_NAME=MAYA
export AR_RESOLVER_NAME=$1
cmake . -B build && cmake --build build --clean-first
cmake --install build
ctest -VV --test-dir build # Run tests