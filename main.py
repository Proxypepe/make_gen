import os
import sys


class AutoGen:
    def __init__(self, main_file: str, compiler: str = "gcc", target: str = None) -> None:
        self.__main_file: str = main_file
        self.__compiler = compiler
        self.__target = target if target else main_file.split('.')[0]
        self.__objects = ""
        self.__code: str = f"CC={self.__compiler}\n" \
                           f"TARGET={self.__target}\n"
        self.__listdir: list[str] = os.listdir()
        self.__included_libs: list[str] = []

    def __get_dep_from_main_file(self):
        with open(self.__main_file) as file:
            for line in file:
                if '"' in line:
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

    def __compile_rule(self):
        for lib in self.__included_libs:
            lib_name = lib.split('.')[0]
            code_file = self.__check_file_extension(lib_name)
            if code_file != "" and lib in self.__listdir:
                pattern = f"{lib_name}.o: {code_file} {lib}\n" \
                          f"\t$(CC) -c code_file\n"
                self.__code += pattern

    def __check_file_extension(self, lib: str):
        extensions = ['.cpp', '.c']
        for extension in extensions:
            if f"{lib}{extension}" in self.__listdir:
                return f"{lib}{extension}"
        return ""

    def __result(self):
        print(self.__code)

    def run(self):
        self.__get_dep_from_main_file()
        self.__init_objects()
        self.__compile_rule()
        self.__result()


def main():
    if sys.argv[1] == "auto" and sys.argv[2] and sys.argv[3]:
        auto = AutoGen(sys.argv[2], sys.argv[3])
        auto.run()


if __name__ == '__main__':
    main()
