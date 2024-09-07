set MAYA_USD_SDK_ROOT=%cd%\dependency\install\maya_usd_sdk
set MAYA_USD_SDK_DEVKIT_ROOT=%cd%\dependency\install\maya_usd_sdk_devkit
set PYTHON_ROOT=%cd%\dependency\install\python
set AR_DCC_NAME=MAYA
set AR_RESOLVER_NAME=%1
cmake . -B build -G %2 -A x64 -T %3
cmake --build build  --clean-first --config Release
cmake --install build