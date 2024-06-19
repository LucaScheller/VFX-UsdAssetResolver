# Clear current session log 
clear
# Source environment (Uncomment lines starting with "export" if you current env does not have these defined.)
export RESOLVER_NAME=cachedResolver
# Clear existing build data and invoke cmake

rm -rf build
rm -rf dist
set -e # Exit on error
cmake . -B build -DCMAKE_VERBOSE_MAKEFILE=ON

# make clean all
cmake --build build --clean-first -DCMAKE_VERBOSE_MAKEFILE=ON
     
# make install        
cmake --install build -DCMAKE_VERBOSE_MAKEFILE=ON
                 
#ctest -VV --test-dir build