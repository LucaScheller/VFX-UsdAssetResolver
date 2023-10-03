REM Clear current session log 
cls
REM Clear existing build data and invoke cmake
rmdir /S /Q build
rmdir /S /Q dist
cmake . -B build -G "Visual Studio 16 2019" -A x64 -T v142
cmake --build build  --clean-first --config Release
cmake --install build