# Clear dirs
rm -R build
rm -R dist
# Invoke cmake
cmake . -B build
cmake --build build --clean-first              # make clean all
cmake --install build                          # make install
