# Requirements

## System dependencies
Currently building on Linux and Windows is documented. We use CMake as our build system and link against Houdini/Maya to avoid having to compile our own version of Usd.

It is also possible to compile against a self-compiled Usd build, this is not covered by this guide though.

VFX DCC vendors try to keep in sync with the versions specified in the [VFX Reference Platform](https://vfxplatform.com), so if something doesn't work, first make sure that your software versions are supported.

```admonish warning
Since the Usd Asset Resolver API changed with the AR 2.0 standard proposed in the [Asset Resolver 2.0 Specification](https://openusd.org/release/wp_ar2.html), you can only compile against Houdini versions 19.5 and higher/Maya versions 2024 and higher.
```

## Linux
```admonish success title=""
| Software               | Website                                                                | Min (Not Tested)     | Max (Tested)  |
|------------------------|------------------------------------------------------------------------|----------------------|---------------|
| gcc                    | [https://gcc.gnu.org](https://gcc.gnu.org/)                            | 11.2.1               | 13.1.1        |
| cmake                  | [https://cmake.org](https://cmake.org/)                                | 3.26.4               | 3.26.4        |
| SideFX Houdini         | [SideFX Houdini](https://www.sidefx.com)                               |  19.5                | 20.5          |
| Autodesk Maya          | [Autodesk Maya](https://www.autodesk.com/ca-en/products/maya/overview) |  2024                | 2024          |
| Autodesk Maya USD SDK  | [Autodesk Maya USD SDK](https://github.com/Autodesk/maya-usd)          |  0.27.0              | 0.27.0        |
```

## Windows
```admonish success title=""
| Software               | Website                                                                            | Min (Not Tested)     | Max (Tested)  |
|------------------------|------------------------------------------------------------------------------------|----------------------|---------------|
|Visual Studio 16 2019   | [https://visualstudio.microsoft.com/vs/](https://visualstudio.microsoft.com/vs/)   | -                    | -             |
|Visual Studio 17 2022   | [https://visualstudio.microsoft.com/vs/](https://visualstudio.microsoft.com/vs/)   | -                    | -             |
| cmake                  | [https://cmake.org](https://cmake.org/)                                            | 3.26.4               | 3.26.4        |
| SideFX Houdini         | [SideFX Houdini](https://www.sidefx.com)                                           |  19.5                | 19.5          |
| Autodesk Maya          | [Autodesk Maya](https://www.autodesk.com/ca-en/products/maya/overview)             |  2024                | 2024          |
| Autodesk Maya USD SDK  | [Autodesk Maya USD SDK](https://github.com/Autodesk/maya-usd)                      |  0.27.0              | 0.27.0        |
```

When compiling against Houdini/Maya on Windows, make sure you use the Visual Studio version that Houdini/Maya was compiled with as noted in the [HDK](https://www.sidefx.com/docs/hdk/_h_d_k__intro__getting_started.html#HDK_Intro_Compiling_Intro_Windows)/[SDK](https://github.com/Autodesk/maya-usd). You'll also need to install the [Visual Studio build tools](https://visualstudio.microsoft.com/downloads/?q=build+tools) that match the Visual Studio release if you want to run everything from the terminal.