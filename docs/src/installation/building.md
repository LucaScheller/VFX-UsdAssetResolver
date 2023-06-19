# Building

# Install a version of Houdini, this script supports H19.5 and higher (See Usd AR 2.0 Spec)
# Here you should edit the <RepoRoot>/CMakeLists.txt to match the Houdini version you want to compile against. 

# Source setup > This appends the install directories to various env vars so that your resolver is sourced
source setup.sh

# Run the build
./build.sh

# Open Houdini
pushd /opt/hfs19.5 > /dev/null
source houdini_setup
popd > /dev/null
{HFS}/bin/houdini -foreground