import os
import sys


class AutoGen:
    def __init__(self, main_file: str = "", compiler: str = "gcc", target: str = None) -> None:
        self.__main_file: str = main_file
        self.__compiler: str = compiler
        self.__target: str = target if target else main_file.split('.')[0]
        self.__objects: str = ""
        self.__code: str = f"CC={self.__compiler}\n"
        self.__clean_code = f"\n.PHONY: clean\n" \
                            f"clean:\n" \
                            f"\trm -rf *.o  {self.__target}\n"
        self.__current_dir: str = os.getcwd()
        self.__included_libs: list[str] = []
        self.__sub_makes = 0

    def __get_dep_from_file(self, file_name: str = "", path: str = "") -> list:
        """
        Reads an input file and collect the dependencies
        Looking for preprocessor instructions '#include' with ""

        :param file_name: str
        :return: list
        """
        if path == "":
            path = self.__current_dir
        file_name = self.__main_file if file_name == "" else file_name
        includes_files = []
        if not os.path.exists(file_name):
            file_name = path + os.sep + file_name
        with open(file_name) as file:
            for line in file:
                if "#include" in line and '"' in line:
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    includes_files.append(line[start:end])
        return includes_files

    def __init_objects(self) -> None:
        """
        Initializes variable TARGET containing the name of the executable file
        Initializes variable OBJS that contains a list of .o files (objects)

        :return: None
        """
        self.__code += f"TARGET={self.__target}\n"
        self.__objects = f"OBJS={self.__target}.o"
        for lib in self.__included_libs:
            lib_name = lib.split('.')[0]
            if os.sep in lib:
                start = lib_name.rfind(os.sep) + 1
                if self.__check_file_extension(lib_name[start:], lib_name[:start - 1]) == "":
                    continue
            else:
                if self.__check_file_extension(lib_name) == "":
                    continue
            self.__objects += f" {lib_name}.o"
        self.__objects += '\n\n'
        self.__code += self.__objects

    def __construct_compile_rules(self, deps: list, lib: str = "") -> None:
        """
        Constructs rules for compiling object files

        :return: None
        """
        lib_name = lib.split('.')[0]
        code_file = self.__check_file_extension(lib_name)
        if code_file != "":
            deps_string = ""
            for dep in deps:
                deps_string += " " + dep
            if code_file == lib:
                lib = ""
            pattern = f"\n{lib_name}.o: {code_file} {lib} {deps_string}\n" \
                      f"\t$(CC) -c {code_file}\n"
            self.__code += pattern

    def __construct_main_compile_rule(self) -> None:
        """
        Writes the default rule for compiling an executable file

        :return: None
        """
        code = "\ncompile: $(OBJS)\n" \
               "\t$(CC) $(OBJS) -o $(TARGET)\n"
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
                self.sub_make(path=path)

    def res(self):
        print(self.__code)

    def write_makefile(self, code: str,  path: str = "") -> None:
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

    def analyze(self, file: str = "") -> str:
        """
        Analyzes files for dependencies
        Recursively traversing files

        :param file: str - filename to parse
        :return: str - returns the name of the library or an empty string
        """
        if file == "":
            file = self.__main_file
        deps = self.__get_dep_from_file(file)
        for dep in deps:
            if dep not in self.__included_libs:
                self.__included_libs.append(dep)
        self.__construct_compile_rules(deps, file)
        if not deps:
            return ""
        for lib in deps:
            self.analyze(lib)
            return lib

    def run(self) -> None:
        """
        Main application loop

        :return: None
        """
        self.__included_libs = self.__get_dep_from_file()
        self.__init_objects()
        self.__construct_main_compile_rule()
        self.analyze()
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
    if sys.argv[1] == "auto" and sys.argv[2] and sys.argv[3]:
        auto = AutoGen(sys.argv[2], sys.argv[3])
        auto.run()


if __name__ == '__main__':
    main()
