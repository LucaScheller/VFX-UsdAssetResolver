set USD_STANDALONE_ROOT=%cd%\dependency\install\usd_standalone
set AR_DCC_NAME=STANDALONE
set AR_RESOLVER_NAME=%1
cmake . -B build -G %2 -A x64 -T %3
cmake --build build  --clean-first --config Release
cmake --install build