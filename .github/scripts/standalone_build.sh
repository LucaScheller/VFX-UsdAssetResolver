repo_root=$(cd .; pwd)
export USD_STANDALONE_ROOT=$repo_root/dependency/install/usd_standalone
export AR_DCC_NAME=STANDALONE
export AR_RESOLVER_NAME=$1
cmake . -B build && cmake --build build --clean-first
cmake --install build
ctest -VV --test-dir build # Run tests