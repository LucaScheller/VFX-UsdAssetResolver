# Requirements

## System dependencies
Currently only building on Linux is documented, building on Windows should work as well though. We use CMake as our build system and link against Houdini to avoid having to compile our own version of Usd.

It is also possible to compile against a self-compiled Usd build, this is not covered by this guide though.

VFX DCC vendors try to keep in sync with the versions specified in the [VFX Reference Platform](https://vfxplatform.com), so if something doesn't work, first make sure that your software versions are supported.

## Linux
```admonish success title=""
| Software        | Website                                          | Min (Not Tested)     | Max (Tested)  |
|-----------------|--------------------------------------------------|----------------------|---------------|
| gcc             | [https://gcc.gnu.org](https://gcc.gnu.org/)      | 11.2.1               | 13.1.1        |
| cmake           | [https://cmake.org](https://cmake.org/)          | 3.26.4               | 3.26.4        |
| SideFX Houdini  | [https://www.sidefx.com](https://www.sidefx.com) |  19.5                | 19.5          |
```

```admonish warning
Since the Usd Asset Resolver API changed with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html), you can only compile against Houdini versions 19.5 and higher.
```