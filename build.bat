REM Clear current session log 
cls
REM Source setup
REM if [ ! $REPO_SOURCED ]
REM then
REM    source setup.sh
REM fi
REM Clear existing build data and invoke cmake
rmdir /S /Q build
rmdir /S /Q dist
cmake . -B build -G "Visual Studio 16 2019" -A x64 -T v142
cmake --build build  --clean-first --config Release
cmake --install build