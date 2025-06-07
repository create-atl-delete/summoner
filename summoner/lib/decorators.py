from inspect import getmembers, isroutine


def method_decorator(decorator):
    def wrapper(cls):
        for name, func in getmembers(cls, isroutine):
            if not name.startswith("_"):
                setattr(cls, name, decorator(cls)(func))
        return cls

    return wrapper
