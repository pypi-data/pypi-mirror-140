try:
    a = 1

    def b():
        print('b')
except:
    pass

print(a)
b()

c = 2


def d(n):
    c = n


d(3)

print(c)
