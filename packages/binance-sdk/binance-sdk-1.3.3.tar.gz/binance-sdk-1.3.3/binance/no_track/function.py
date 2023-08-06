def a(a=1, b=2, c=3, *args, **kwargs):
    print(a, b, c, args, kwargs)


def b(*arg, **kwargs):
    a(*arg, **kwargs)


b(1, 1, 1, 4, d=3)

b()
# def c():
#     return 1, 2

# print(c())
