# Simple Makefile generator
![Test workflow](https://github.com/Proxypepe/makefile_generator/actions/workflows/examples.yml/badge.svg)

Simple code generator. Works with small C / C ++ projects. Analyzes the dependencies of the main file and its dependency files. Works correctly if all files are in the same directory.

## How to use

Requires only python interpreter 3.8 and above.  
Currently, only auto mod is available.  
```sh
python3 main.py auto {target file} {compiler}
```
Target file - program entry point file. You need to specify the path from the script.
compiler - specify the compiler you want to use