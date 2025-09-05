REM Clear current session log 
cls
REM Source environment (Uncomment lines starting with "set" if you current env does not have these defined.)
REM set HFS=C:\Program Files\Side Effects Software\<InsertHoudiniVersion>
REM Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'cachedResolver'/'httpResolver'
REM set AR_RESOLVER_NAME=cachedResolver
REM Define App
REM set AR_DCC_NAME=HOUDINI
REM Clear existing build data and invoke cmake
rmdir /S /Q build
rmdir /S /Q dist
REM Make sure to match the correct VS version the DCC was built with
cmake . -B build -G "Visual Studio 17 2022" -A x64 -T v143
cmake --build build  --clean-first --config Release
cmake --install build