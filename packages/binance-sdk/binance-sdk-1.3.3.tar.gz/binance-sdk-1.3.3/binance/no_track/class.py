# class sampleclass:
#     # count = 0     # class attribute
#     # count2 = 0

#     def __init__ (self):
#         pass

#     def increase(self):
#         sampleclass.count += 1
#         self.count2 += 1

# setattr(sampleclass, 'count', 0)
# sampleclass.count2 = 0

# # Calling increase() on an object
# s1 = sampleclass()
# s1.increase()
# print('s1.count', s1.count)
# print('s1.count2', s1.count2)

# # Calling increase on one more
# # object
# s2 = sampleclass()
# s2.increase()
# print('s1.count', s2.count)
# print('s1.count2', s2.count2)

# print('sampleclass.count', getattr(sampleclass, 'count'))
# print('sampleclass.count2', sampleclass.count2)

# a = 1
# print(++ a)

# print('=====================')

# class A:
#     A = 'log'
#     def __init__(self):
#         self.a = 'log'

# def log(self):
#     return self.a

# def staticLog(cls):
#     return cls.A

# # A.log = log
# A.log = lambda self: self.a
# A.staticLog = classmethod(staticLog)

# print(A().log())
# print(A.staticLog())

# from abc import ABC, abstractmethod


class A(object):
    @property
    def a(self):
        return 1


class B(A):
    pass


b = B()

# b.b = 2

print(b.a)
# print(b.b)
