import os
import argparse
import pathlib


class AutoGen:
    def __init__(self, main_file: str = "", compiler: str = "gcc", target: str = None) -> None:
        self.__main_file: str = main_file
        self.__compiler: str = compiler
        self.__check_curr_dir()
        self.__target: str = target if target else self.__main_file.split('.')[0]
        self.__objects: str = f"OBJS={self.__target}.o"
        self.__flags: list[str] = []
        self.__flags_string = ""
        self.__code: str = f"CC={self.__compiler}\n" \
                           f"TARGET={self.__target}\n"
        self.__clean_code = f"\n.PHONY: clean\n" \
                            f"clean:\n" \
                            f"\trm -rf *.o  {self.__target}\n"
        self.__current_dir: str = os.getcwd()
        self.__included_libs: list[str] = []
        self.__included_libs_all: list[str] = []
        self.__written_lib: list[str] = []
        self.__written_dirs = []
        self.__sub_makes = 0

    def __check_curr_dir(self):
        if os.sep in self.__main_file:
            start = self.__main_file.rfind(os.sep) + 1
            path = os.getcwd() + os.sep + self.__main_file[:start - 1]
            self.__main_file = self.__main_file[start:]
            os.chdir(path)

    def __get_dep_from_file(self, file_name: str = "", path: str = "") -> list:
        """
        Reads an input file and collect the dependencies
        Looking for preprocessor instructions '#include' with ""
        :param file_name: str
        :param path: str
        :return: list
        """
        if path == "":
            path = self.__current_dir
        file_name = self.__main_file if file_name == "" else file_name
        includes_files = []

        if not pathlib.Path(file_name).exists():
            print(path)
            file_name = path + os.sep + file_name
            print("fff", file_name)
        with open(file_name) as file:
            for line in file:
                if "#include" in line and '"' in line:
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    includes_files.append(line[start:end])
        return includes_files

    def __get_all_deps(self, file="", path=""):
        if file == "":
            file = self.__main_file
        print(f"file: {file} path: {path}")
        if path == "":
            start = file.rfind(os.sep) + 1
            path = file[:start]
        print(f"all file: {file} path: {path}")
        deps = self.__get_dep_from_file(file, path)
        for dep in deps:
            if dep not in self.__included_libs_all:
                self.__included_libs_all.append(dep)
            self.__get_all_deps(dep, path)

    def __init_objects(self) -> None:
        """
        Initializes variable TARGET containing the name of the executable file
        Initializes variable OBJS that contains a list of .o files (objects)
        :return: None
        """
        self.__get_all_deps()
        for lib in self.__included_libs_all:
            lib_name = lib.split('.')[0]
            if os.sep in lib:
                start = lib_name.rfind(os.sep) + 1
                if self.__check_file_extension(lib_name[start:], lib_name[:start - 1]) == "":
                    continue
            else:
                if self.__check_file_extension(lib_name) == "":
                    continue
            self.__objects += f" {lib_name}.o"
        self.__code += f"{self.__objects}\n\n"

    def __construct_compile_rules(self, deps: list, lib: str = "") -> None:
        """
        Constructs rules for compiling object files
        :return: None
        """
        lib_name = lib.split('.')[0]
        code_file = self.__check_file_extension(lib_name)
        if code_file != "" and lib_name not in self.__written_lib:
            deps_string = ""
            for dep in deps:
                deps_string += " " + dep
            if code_file == lib:
                lib = ""
            pattern = f"\n{lib_name}.o: {code_file} {lib} {deps_string}\n" \
                      f"\t$(CC){self.__flags_string} -c {code_file}\n"
            self.__code += pattern
            self.__written_lib.append(lib_name)

    def __construct_main_compile_rule(self) -> None:
        """
        Writes the default rule for compiling an executable file
        :return: None
        """
        code = f"\ncompile: $(OBJS)\n" \
               f"\t$(CC){self.__flags_string} $(OBJS) -o $(TARGET)\n"
        self.__code += code

    def __check_file_extension(self, lib: str, path: str = "") -> str:
        """
        Search for a code file with a given library name in a directory
        :param lib: str - library name
        :param path: str - path to dictionary
        :return: str
        """
        if path == "":
            path = self.__current_dir
        extensions = ['.cpp', '.c']
        for extension in extensions:
            if f"{lib}{extension}" in os.listdir(path):
                return f"{lib}{extension}"
        return ""

    def __write_test_section(self) -> None:
        """
        Adds code to execute the target file
        :return: None
        """
        test_section = "\n.PHONY: run\n" \
                       "run:\n" \
                       f"\t./{self.__target}\n"
        self.__code += test_section

    def __write_flags(self) -> None:
        flags = 'FLAGS='
        for flag in self.__flags:
            flags += f' {flag}'
        flags += '\n'
        self.__flags_string = ' $(FLAGS)'
        self.__code += flags

    def __check_sub_makefiles(self) -> None:
        """
        Checks subdirectories and creates a Makefile for each directory
        :return: None
        """
        for lib in self.__included_libs:
            splited_lib = lib.split(os.sep)
            if len(splited_lib) > 1:
                path = ""
                for part in splited_lib[:-1]:
                    path += part + os.sep
                if path not in self.__written_dirs:
                    self.__written_dirs.append(path)
                    self.sub_make(path=path)

    def res(self):
        print(self.__code)

    def write_makefile(self, code: str, path: str = "") -> None:
        """
        Writes code to a Makefile
        :param code: str - code for Makefile
        :param path: str - path to Makefile
        :return: None
        """
        if path != "":
            path += os.sep
        with open(f"{path}Makefile", 'w') as file:
            file.write(code)

    def analyze(self, file: str = "") -> None:
        """
        Analyzes files for dependencies
        Recursively traversing files
        :param file: str - filename to parse
        :return: None
        """
        if file == "":
            file = self.__main_file
        if os.sep not in file:
            deps = self.__get_dep_from_file(file)
            self.__construct_compile_rules(deps, file)
            for dep in deps:
                if dep not in self.__included_libs:
                    self.__included_libs.append(dep)
                self.analyze(dep)

    def run(self) -> None:
        """
        Main application loop
        :return: None
        """
        self.__included_libs = self.__get_dep_from_file()
        self.__init_objects()
        if self.__flags:
            self.__write_flags()
        self.analyze()
        self.__construct_main_compile_rule()
        self.__check_sub_makefiles()
        self.__code += self.__clean_code
        self.__write_test_section()
        self.write_makefile(self.__code)

    def sub_make(self, path: str) -> None:
        """
        Writes rules for each directory and creates a Makefile
        :param path: str - path to a directory
        :return:
        """
        self.__sub_makes += 1
        code = f"\npath{self.__sub_makes}:\n" \
               f"\tcd {path} && $(MAKE)\n"
        self.__clean_code += f"\tcd {path} && $(MAKE) clean\n"
        self.__code += code
        a = AutoGen(compiler=self.__compiler)
        a.path = path
        for lib in self.__included_libs:
            if lib.startswith(path):
                a.analyze(lib.split(os.sep)[-1])
        a.__code += a.__clean_code
        a.write_makefile(a.__code, path)

    def add_flags(self, flags: list):
        self.__flags = flags

    @property
    def path(self) -> str:
        return self.__current_dir

    @path.setter
    def path(self, path: str) -> None:
        self.__current_dir = path

    @property
    def libs(self) -> list:
        return self.__included_libs

    @libs.setter
    def libs(self, include_libs) -> None:
        self.__included_libs = include_libs


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mode', type=str, required=True,
                        help="")

    parser.add_argument('-t', '--target', type=str, required=True,
                        help="C or C++ file with main function")

    parser.add_argument('-c', '--compiler', type=str, action='store', required=False,
                        default='gcc', help="Compiler selection")

    parser.add_argument('-o', '--obj', type=str, action='store', required=False,
                        help="Compiler selection")

    parser.add_argument('-f', '--flags', required=False,
                        nargs='*', help="Spacial compilation flags")

    args = parser.parse_args()

    if args.mode == "auto" and args.target:
        target_file = args.target
        program_compiler = args.compiler
        object_file = args.obj

        auto = AutoGen(main_file=target_file, compiler=program_compiler, target=object_file)
        if args.flags:
            auto.add_flags(args.flags)
        auto.run()


if __name__ == '__main__':
    main()
