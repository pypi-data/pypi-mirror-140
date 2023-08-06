def ping_decorator(func):
    def wrapper() -> str:
        result = func()
        if result:
            if result == "pong":
                return result
            elif result is True:
                return "pong"
        return ""

    return wrapper


def exploit_decorator(func):
    def wrapper() -> int:
        result = func()
        if result:
            if result == 1:
                return result
            if result is True:
                return 1
        return 0
    return wrapper
