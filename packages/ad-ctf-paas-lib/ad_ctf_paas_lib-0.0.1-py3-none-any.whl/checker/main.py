import argparse
import sys


class Actions:
    def __init__(self):
        self.functions = {}

    def register(self, func):
        def wrapper(action):
            self.functions[action] = func

        return wrapper

    def ping(self, func):
        self.functions["ping"] = func

    def put(self, func):
        self.functions["put"] = func

    def get(self, func):
        self.functions["get"] = func

    def exploit(self, func):
        self.functions["exploit"] = func


class Checker(Actions):
    def __init__(self):
        super().__init__()
        self.address = "localhost"
        self.flag = None
        self.uniq_value = None

    def run_function(self, action):
        try:
            result = self.functions[action]()
            if result:
                print(result)
                return 0
            else:
                return 1
        except Exception as e:
            print(e)
            return 1

    def run(self):
        parser = argparse.ArgumentParser(prog='myprogram')
        parser.add_argument("action", help="choose function")
        parser.add_argument("address", help="ip or domain")
        parser.add_argument("value", nargs='?', help="enter flag or uniq value", default=None)
        args = parser.parse_args()
        if args.action not in self.functions:
            raise Exception(f'Cannot find function "{args.action}" in registered functions')
        self.address = args.address
        self.flag = self.uniq_value = args.value
        exit(self.run_function(action=args.action))
        # if len(sys.argv) < 2:
        #     raise Exception('No arguments')
        #
        # if sys.argv[1] in self.functions:
        #     self.functions[sys.argv[1]](*sys.argv)
        # else:
        #


class ArgsParser:
    def __init__(self):
        pass
