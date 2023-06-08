This repo holds Usd Asset Resolvers:
- File Resolver:
    A file system based resolver. This resolver is very similar to the default resolver, except that it has the following extra features:
    - ToDo
- Python Resolver:
    This is a prototyping resolver using Python. This should not be used in production as it is not multithreaded due to Python's Global Interpreter Lock (GIL).
    It can be used to quickly inspect resolve calls and to setup prototypes of resolvers that can then later be re-written in C++ as it is easier to code database related pipelines in Python.

Install instructions:
- Follow the instructions in the install.md file (Currently only Linux is supported).

This repo is still under construction, code is provided as is with no support :)
