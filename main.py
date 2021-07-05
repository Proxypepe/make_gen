import os
import sys


class AutoGen:
    def __init__(self, main_file: str = "", compiler: str = "gcc", target: str = None) -> None:
        self.__main_file: str = main_file
        self.__compiler: str = compiler
        self.__target: str = target if target else main_file.split('.')[0]
        self.__objects: str = ""
        self.__code: str = f"CC={self.__compiler}\n"
        self.__current_dir: str = os.getcwd()
        self.__all_deps: list[str] = []
        self.__included_libs: list[str] = []
        self.__sub_makes = 0

    def __get_dep_from_main_file(self) -> None:
        """
        Reads target file and collect the dependencies.
        Looking for preprocessor instructions '#include' with "".
        :return: None
        """
        with open(self.__main_file) as file:
            for line in file:
                if "#include" in line and '"' in line:
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    self.__included_libs.append(line[start:end])

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
            self.__objects += f" {lib_name}.o"
        self.__objects += '\n\n'
        self.__code += self.__objects

    def __construct_compile_rules(self) -> None:
        """
        Constructs rules for files with code
        :return: None
        """
        for lib in self.__included_libs:
            lib_name = lib.split('.')[0]
            code_file = self.__check_file_extension(lib_name)
            self.__all_deps.append(code_file)
            if code_file != "":
                pattern = f"\n{lib_name}.o: {code_file} {lib}\n" \
                          f"\t$(CC) -c {code_file}\n"
                self.__code += pattern

    def __construct_compile_main_file(self):
        deps = ""
        for code_file in self.__all_deps:
            deps += " " + code_file
        for lib in self.__included_libs:
            deps += " " + lib
        code = f"\n{self.__target}.o: {self.__main_file} {deps}\n" \
               f"\t$(CC) -c {self.__main_file}\n"
        self.__code += code

    def __construct_main_compile_rule(self):
        code = "\ncompile: $(OBJS)\n" \
               "\t$(CC) $(OBJS) -o $(TARGET)\n"
        self.__code += code

    def __check_file_extension(self, lib: str):
        extensions = ['.cpp', '.c']
        for extension in extensions:
            if f"{lib}{extension}" in os.listdir(self.__current_dir):
                return f"{lib}{extension}"
        return ""

    def __write_clean_section(self):
        clean_part = f"\n.PHONY: clean\n" \
               f"clean:\n" \
               f"\trm -rf *.o  {self.__target}\n"
        self.__code += clean_part

    def __write_test_section(self) -> None:
        test_section = "\n.PHONY: run\n" \
                       "run:\n" \
                       f"\t./{self.__target}\n"
        self.__code += test_section

    def __check_sub_makefiles(self) -> None:
        for lib in self.__included_libs:
            splited_lib = lib.split(os.sep)
            if len(splited_lib) > 1:
                path = ""
                for part in splited_lib[:-1]:
                    path += part + os.sep
                self.sub_make(path=path)

    def __res(self):
        print(self.__code)

    def write_makefile(self, code: str,  path: str = "") -> None:
        if path != "":
            path += os.sep
        with open(f"{path}Makefile", 'w') as file:
            file.write(code)

    def sub_make(self, path: str) -> None:
        self.__sub_makes += 1
        code = f"\npath{1}:\n" \
               f"\tcd {path} && $(MAKE)\n"
        self.__code += code
        a = AutoGen(compiler=self.__compiler)
        a.path = path
        for lib in self.__included_libs:
            if lib.startswith(path):
                a.__included_libs.append(lib.split(os.sep)[-1])
        a.__construct_compile_rules()
        a.__write_clean_section()
        a.write_makefile(a.__code, path)

    def run(self) -> None:
        self.__get_dep_from_main_file()
        self.__init_objects()
        self.__construct_main_compile_rule()
        self.__construct_compile_rules()
        self.__check_sub_makefiles()
        self.__construct_compile_main_file()
        self.__write_clean_section()
        self.__write_test_section()
        self.write_makefile(self.__code)

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
