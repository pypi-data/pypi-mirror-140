def a(s, *arg):
    return s % arg


print(a('`%s` + %s = %s', 1, 2, 3))

print(a('2'))

l = [1, 2, 3]
print([x + 1 for x in l])
