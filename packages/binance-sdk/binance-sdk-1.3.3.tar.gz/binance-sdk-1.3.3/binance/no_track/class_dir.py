class A:
    pass


def foo(self):
    return 1


A.foo = foo

a = A()

print(a.foo())
