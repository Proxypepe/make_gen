# Simple Makefile generator
![Test workflow](https://github.com/Proxypepe/makefile_generator/actions/workflows/examples.yml/badge.svg)
## About
Simple code generator. Works with small C / C ++ projects. Analyzes the dependencies of the main file and its dependency files. Works correctly if all files are in the same directory.

## How to use

Requires only python interpreter 3.8 and above.  
Currently, only auto mod is available.  
```sh
python3 main.py -m auto -t {target file} -c {compiler}
```

```sh
usage: main.py -m MODE -t TARGET [-c COMPILER] [-o OBJ] [-f [FLAGS [FLAGS ...]]]
```

optional arguments:
``` 
-h, --help show this help message and exit  
  -m, --mode  
            Now only auto mode is available  
  -t, --target  
             Program entry point file. You need to specify the path from the script. 
  -c COMPILER, --compiler COMPILER  
            Specify the compiler you want to use 
  -o, --obj     
            Result executable file  
  -f, --flags  
            Spacial compilation flags
```