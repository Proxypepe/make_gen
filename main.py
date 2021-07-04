import os
import sys


class AutoGen:
    def __init__(self, main_file: str, compiler: str = "gcc", target: str = None) -> None:
        self.__main_file: str = main_file
        self.__compiler = compiler
        self.__target = target if target else main_file.split('.')[0]
        self.__objects = ""
        self.__all_deps = []
        self.__code: str = f"CC={self.__compiler}\n" \
                           f"TARGET={self.__target}\n"
        self.__listdir: list[str] = os.listdir()
        self.__included_libs: list[str] = []

    def __get_dep_from_main_file(self):
        with open(self.__main_file) as file:
            for line in file:
                if line.startswith("#include") and '"' in line:
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    self.__included_libs.append(line[start:end])

    def __init_objects(self):
        self.__objects = f"OBJS={self.__target}.o"
        for lib in self.__included_libs:
            lib_name = lib.split('.')[0]
            self.__objects += f" {lib_name}.o"
        self.__objects += '\n\n'
        self.__code += self.__objects

    def __compile_rules(self):
        for lib in self.__included_libs:
            lib_name = lib.split('.')[0]
            code_file = self.__check_file_extension(lib_name)
            self.__all_deps.append(code_file)
            if code_file != "":
                pattern = f"{lib_name}.o: {code_file} {lib}\n" \
                          f"\t$(CC) -c {code_file}\n\n"
                self.__code += pattern

    def __compile_main_file(self):
        deps = ""
        for code_file in self.__all_deps:
            deps += " " + code_file
        for lib in self.__included_libs:
            deps += " " + lib
        code = f"{self.__target}.o: {self.__main_file} {deps}\n" \
               f"\t$(CC) -c {self.__main_file}\n\n"
        self.__code += code

    def __main_compile_rule(self):
        code = "compile: $(OBJS)\n" \
               "\t$(CC) $(OBJS) -o $(TARGET)\n\n"
        self.__code += code

    def __check_file_extension(self, lib: str):
        # TODO check other folders
        extensions = ['.cpp', '.c']
        for extension in extensions:
            if f"{lib}{extension}" in self.__listdir:
                return f"{lib}{extension}"
        return ""

    def __write_clean_section(self):
        clean_part = f"\n\n.PHONY: clean\n" \
               f"clean:\n" \
               f"\trm *.o  {self.__target}"
        self.__code += clean_part

    def __write_test_section(self):
        test_section = "\n\n.PHONY: run\n" \
                       "run:\n" \
                       f"\t./{self.__target}"
        self.__code += test_section

    def __res(self):
        print(self.__code)

    def run(self):
        self.__get_dep_from_main_file()
        self.__init_objects()
        self.__main_compile_rule()
        self.__compile_rules()
        self.__compile_main_file()
        self.__write_clean_section()
        self.__write_test_section()
        self.__res()


def main():
    if sys.argv[1] == "auto" and sys.argv[2] and sys.argv[3]:
        auto = AutoGen(sys.argv[2], sys.argv[3])
        auto.run()


if __name__ == '__main__':
    main()
