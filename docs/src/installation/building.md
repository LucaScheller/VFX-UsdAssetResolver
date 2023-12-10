# Building
Currently we support building against Houdini on Linux and Windows. If you don't want to self-compile, you can also download pre-compiled builds on our [release page](https://github.com/LucaScheller/VFX-UsdAssetResolver/releases). To load the resolver, you must specify a few environment variables, see our [Resolvers > Environment Variables](../resolvers/overview.md#environment-variables) section for more details. 

## Setting up our build environment
After installing the [requirements](./requirements.md), we first need to set a couple of environment variables that our cmake file depends on.

### Using our convenience setup script
On Linux we provide a bash script that you can source that sets up our development environment. This sets a few environment variables needed to build the resolver as well as for Houdini to load it.
This can be done by running the following from the source directory:
~~~admonish info title=""
```bash
source setup.sh
```
~~~

In the [setup.sh](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/setup.sh) file you can define what resolver to compile by setting the `RESOLVER_NAME` variable to one of the resolvers listed in [resolvers](../resolvers/overview.md) in camelCase syntax (for example `fileResolver` or `pythonResolver`). Here you'll also have to define what Houdini version to compile against.

It will then automatically set the `PATH`, `PYTHONPATH`, `PXR_PLUGINPATH_NAME` and `LD_LIBRARY_PATH` environment variables to the correct paths so that after your run the compile, the resolver will be loaded correctly (e.g. if you launch Houdini via `houdinifx`, it will load everything correctly). The build process also logs this information again.

By default it also sets the `TF_DEBUG` env var to `AR_RESOLVER_INIT` so that you'll get logs of what resolver is loaded by USD's plugin system, which you can use to verify that everything is working correctly.

### Manually setting up the environment
If you don't want to use our convenience script, you can also setup the environment manually.

~~~admonish info title=""
```bash
# Linux
export HFS=<PathToHoudiniRoot> # For example "/opt/hfs<HoudiniVersion>"
export RESOLVER_NAME=fileResolver
# Windows
set HFS=<PathToHoudiniRoot> # For example "C:\Program Files\Side Effects Software\<HoudiniVersion>"
set RESOLVER_NAME=fileResolver
```
~~~

## Running the build
To run the build, run:

~~~admonish warning title="Houdini GCC ABI Change"
Starting with Houdini 20, SideFX is offering gcc 11 builds that don't use the old Lib C ABI. Our automatic GitHub builds make use of this starting Houdini 20 and upwards.
To make our CMake script still work with H19.5, we automatically switch to use the old ABI, if the Houdini version 19.5 is in the Houdini root folder path.

If you want to still build against gcc 9 (with the old Lib C ABI) with Houdini 20 and upwards, you'll need to set `_GLIBCXX_USE_CXX11_ABI=0` as described below and make sure you have the right Houdini build installed.

If you want to enforce it manually, you'll need to update the line below in our main CMakeLists.txt file. 
For gcc 9 builds Houdini uses the old Lib C ABI, so you'll need to set it to `_GLIBCXX_USE_CXX11_ABI=0`, for gcc 11 to `_GLIBCXX_USE_CXX11_ABI=1`.

See the official [Release Notes](https://www.sidefx.com/docs/houdini/news/20/platforms.html) for more information.
```bash
    ...
    add_compile_definitions(_GLIBCXX_USE_CXX11_ABI=0)
    ...
```
~~~

~~~admonish info title=""
```bash
# Linux
./build.sh
# Windows
build.bat
```
~~~

The `build.sh/.bat` files also contain (commented out) the environment definition part above, so alternatively just comment out the lines and you are good to go.

## Testing the build
Unit tests are automatically run post-build on Linux using the Houdini version you are using. You can find each resolvers tests in its respective src/<ResolverName>/testenv folder.

Alternatively you can run Houdini and check if the resolver executes correctly. If you didn't use our convenience script as noted above, you'll have to specify a few environment variables, so that our plugin is correctly detected by USD.

Head over to our [Resolvers > Environment Variables](../resolvers/overview.md#environment-variables) section on how to do this.

After that everything should run smoothly, you can try loading the examples in the "files" directory or work through our [example setup](../resolvers/ExampleSetup/overview.md) section for a simple production example.

## Customize build
If you want to further configure the build, you can head into the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) in the root of this repo. In the first section of the file, you can configure various things, like the environment variables that the resolvers use, Python module namespaces and what resolvers to compile.
This is a standard `CMakeLists.txt` file that you can also configure via [CMake-GUI](https://cmake.org/cmake/help/latest/manual/cmake-gui.1.html). If you don't want to use the `build.sh` bash script, you can also configure and compile this project like any other C++ project via this file.

# Documentation
If you want to locally build this documentation, you'll have to download [mdBook](https://github.com/rust-lang/mdBook) and [mdBook-admonish](https://github.com/tommilligan/mdbook-admonish) and add their parent directories to the `PATH`env variable so that the executables are found.

You can do this via bash (after running `source setup.sh`):
~~~admonish info title=""
```bash
export MDBOOK_VERSION="0.4.28"
export MDBOOK_ADMONISH_VERSION="1.9.0"
curl -L https://github.com/rust-lang/mdBook/releases/download/v$MDBOOK_VERSION/mdbook-v$MDBOOK_VERSION-x86_64-unknown-linux-gnu.tar.gz | tar xz -C ${REPO_ROOT}/tools
curl -L https://github.com/tommilligan/mdbook-admonish/releases/download/v$MDBOOK_ADMONISH_VERSION/mdbook-admonish-v$MDBOOK_ADMONISH_VERSION-x86_64-unknown-linux-gnu.tar.gz | tar xz -C ${REPO_ROOT}/tools
export PATH=${REPO_ROOT}/tools:$PATH
```
~~~

You then can just run the following to build the documentation in html format:
~~~admonish info title=""
```bash
./docs.sh
```
~~~

The documentation will then be built in docs/book.