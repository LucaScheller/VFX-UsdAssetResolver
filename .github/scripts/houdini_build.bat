set HFS=C:\Program Files\Side Effects Software\Houdini
set AR_DCC_NAME=HOUDINI
set AR_RESOLVER_NAME=%1
cmake . -B build -G "Visual Studio 16 2019" -A x64 -T v142
cmake --build build  --clean-first --config Release
cmake --install build