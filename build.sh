# Clear current session log 
clear
# Source environment (Uncomment lines starting with "export" if you current env does not have these defined.)
export RESOLVER_NAME=cachedResolver
# Clear existing build data and invoke cmake

rm -rf build
rm -rf dist
set -e # Exit on error
cmake . -B build

# make clean all
cmake --build build --clean-first -v
     
# make install        
cmake --install build
                 
# ctest -VV --test-dir build