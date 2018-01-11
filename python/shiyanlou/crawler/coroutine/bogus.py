'''
coroutine理解:
1. generator and coroutine are different concepts, generator produce data, and coroutine consume data;
2. generator and coroutine both use key word "yield", yield expression and yield assigment are all legal;
3. generator和coroutine的执行顺序都是从上一个yield语句（或function entry point)到下一个yield语句；
4. 函数中（似乎）会记录上次执行到的yield语句的位置（当存在多个yield语句时)，无论是何种类型的调用语句（迭代iterator或send），都是从上一个yield语句执行到下一个yield语句。
'''
def countdown(n):
    print("Counting down from {}".format(n))
    while n>=0:
        newvalue=(yield n)
        # yield n
        # print("Running one while with n={}".format(n))
        # newvalue=(yield)
        print("Running one while with newvalue={},n={}".format(newvalue,n))
        if newvalue is not None:
            n=newvalue
        else:
            n-=1

c=countdown(5)
for n in c:
    print(n)
    if n==5:
        c.send(3)
        c.send(2)
