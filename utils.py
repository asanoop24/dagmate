from functools import wraps

from typing import get_type_hints


def factory(*args, **kwargs):
    def inner(*args, **kwargs):
        for a in args:
            print(a)
        # if name == "add":
        #     s = 0
        #     for a in args:
        #         s += a
        #     return s
        # elif name == "multiply":
        #     s = 1
        #     for a in args:
        #         s *= a
        #     return s

    return inner


class Factory:
    def __init__(self, func_name, *func_args, **func_kwargs):
        self.__name__ = func_name
        self.args = func_args
        self.kwargs = func_kwargs

    # def func(self, *self.args, **self.kwargs):
    #     for a in self.args:
    #         print(a)


import inspect

if __name__ == "__main__":
    a = factory("x", "y")
    print(a)
    print(inspect.getfullargspec(a))

    # f = factory("func","x","y")
    # print(dir(f))
    # print(factory.__code__.co_argcount)
    # print(f.__code__.co_argcount)
    # print(func.__code__.co_argcount)
    # print(func.__code__.co_varnames)
    # func_names = ["f1","f2","f3"]
    # for func_name in func_names:
    #     func = factory(func_name)

    # f1 = Factory("f1","X","Y").func
    # f1 = factory("f1","Y","2")
    # f2 = factory("f2","Y","2")
    # f3 = factory("f2","Z","3")
    # print(f1.__name__)
    # print(f1)
    # print(f3)
    # f1(1,4)
    # f2()
    # print(dir(f1))
