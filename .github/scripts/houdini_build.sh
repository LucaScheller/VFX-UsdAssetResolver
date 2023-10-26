pushd /opt/hfs > /dev/null && source houdini_setup && popd > /dev/null
export RESOLVER_NAME=$1
cmake . -B build && cmake --build build --clean-first
cmake --install build
ctest -VV --test-dir build # Run tests