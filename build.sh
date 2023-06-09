# Clear existing build data and invoke cmake
rm -R build
rm -R dist
cmake . -B build
cmake --build build --clean-first              # make clean all
cmake --install build                          # make install
