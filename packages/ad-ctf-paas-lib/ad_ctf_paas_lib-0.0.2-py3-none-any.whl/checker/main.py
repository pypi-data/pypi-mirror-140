import argparse
from collections import defaultdict


class Actions:
    def __init__(self):
        self.functions = defaultdict(list)

    def register(self, func):
        def wrapper(action):
            self.functions[action].append(func)

        return wrapper

    def ping(self, func):
        self.functions["ping"].append(func)

    def put(self, func):
        self.functions["put"].append(func)

    def get(self, func):
        self.functions["get"].append(func)

    def exploit(self, func):
        self.functions["exploit"].append(func)


class Checker(Actions):
    def __init__(self):
        super().__init__()
        self.address = "localhost"
        self.flag = None
        self.uniq_value = None

    def run_function(self, action, counter):
        try:
            result = self.functions[action][counter]()
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
        parser.add_argument("counter", help="counter for multiple flags")
        parser.add_argument("action", help="choose function")
        parser.add_argument("address", help="ip or domain")
        parser.add_argument("value", nargs='?', help="enter flag or uniq value", default=None)
        args = parser.parse_args()
        if args.action not in self.functions:
            raise Exception(f'Cannot find function "{args.action}" in registered functions')
        self.address = args.address
        self.flag = self.uniq_value = args.value
        counter = int(args.counter)
        exit(self.run_function(action=args.action, counter=counter))


class ArgsParser:
    def __init__(self):
        pass
