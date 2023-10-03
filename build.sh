# Clear current session log 
clear
# Source environment (Uncomment lines starting with "export" if you current env does not have these defined.)
# export HFS=C:\Program Files\Side Effects Software\<InsertHoudiniVersion>
# Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'hybridResolver'
# export RESOLVER_NAME=fileResolver
# Clear existing build data and invoke cmake
rm -R build
rm -R dist
cmake . -B build
cmake --build build --clean-first              # make clean all
cmake --install build                          # make install
