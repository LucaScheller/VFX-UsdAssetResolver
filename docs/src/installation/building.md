# Building

After installing the [requirements](./requirements.md), we need to first source our development environment.

This can be done by running the following from the source directory:
```bash
source setup.sh
```

In the [setup.sh](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/setup.sh) file you can define what resolver to compile by setting the `RESOLVER_NAME` variable to one of the resolvers listed in [resolvers](../resolvers/overview.md) in camelCase syntax (for example `fileResolver` or `pythonResolver`).

```admonish important
Here you'll also have to define what Houdini version to compile against.
```


It will then automatically set the `PATH`, `PYTHONPATH`, `PXR_PLUGINPATH_NAME` and `LD_LIBRARY_PATH` environment variables to the correct paths so that after your run the compile, the resolver will be loaded correctly (e.g. if you launch Houdini via `houdinifx`, it will load everything correctly). The build process also logs this information again.

To run the build, run:

```bash
./build.sh
```

By default it also sets the `TF_DEBUG` env var to `<ResolverName>_RESOLVER` so that you'll get debug logs of what the resolver is doing. Check out the debug codes section of the resolvers for more information.

If you want to further configure the build, you can head into the [CMakeLists.txt](https://github.com/LucaScheller/VFX-UsdAssetResolver/blob/main/CMakeLists.txt) in the root of this repo. In the first section of the file, you can configure various things, like the environment variables that the resolvers use, Python module namespaces and what resolvers to compile.
This is a standard `CMakeLists.txt` file that you can also configure via [CMake-GUI](https://cmake.org/cmake/help/latest/manual/cmake-gui.1.html). If you don't want to use the `build.sh` bash script, you can also configure and compile this project like any other C++ project via this file.

If you want to change the resolver names, you'll have to additionally edit the `CMakeLists.txt` files in the corresponding resolver folder by un-commenting the following line in the beginning of the file:
```cmake
add_compile_definitions(<ResolverName>=${AR_<RESOLVERNAME>_USD_CXX_CLASS_NAME})
```
This is considered experimental and is not guaranteed to work. It is easier to just rename all Python/C++ class via a quick search & replace.

# Documentation

If you want to locally build this documentation, you'll have to download [mdBook](https://github.com/rust-lang/mdBook) and [mdBook-admonish](https://github.com/tommilligan/mdbook-admonish) and add their parent directories to the `PATH`env variable so that the executables are found.

You can do this via bash (after running `source setup.sh`):
```bash
export MDBOOK_VERSION="0.4.28"
export MDBOOK_ADMONISH_VERSION="1.9.0"
curl -L https://github.com/rust-lang/mdBook/releases/download/v$MDBOOK_VERSION/mdbook-v$MDBOOK_VERSION-x86_64-unknown-linux-gnu.tar.gz | tar xz -C ${REPO_ROOT}/tools
curl -L https://github.com/tommilligan/mdbook-admonish/releases/download/v$MDBOOK_ADMONISH_VERSION/mdbook-admonish-v$MDBOOK_ADMONISH_VERSION-x86_64-unknown-linux-gnu.tar.gz | tar xz -C ${REPO_ROOT}/tools
export PATH=${REPO_ROOT}/tools:$PATH
```

You then can just run the following to build the documentation in html format:
```bash
./docs.sh
```

The documentation will then be built in docs/book.