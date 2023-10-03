REM Clear current session log 
cls
REM Source environment (Uncomment lines starting with "set" if you current env does not have these defined.)
REM set HFS=C:\Program Files\Side Effects Software\<InsertHoudiniVersion>
REM Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'hybridResolver'
REM set RESOLVER_NAME=fileResolver
REM Clear existing build data and invoke cmake
rmdir /S /Q build
rmdir /S /Q dist
cmake . -B build -G "Visual Studio 16 2019" -A x64 -T v142
cmake --build build  --clean-first --config Release
cmake --install build