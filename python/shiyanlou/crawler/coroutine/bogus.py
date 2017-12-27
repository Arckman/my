def countdown(n):
    print("Counting down from {}".format(n))
    while n>=0:
        # newvalue=(yield n)
        yield n
        print("Running one while with n={}".format(n))
        newvalue=(yield)
        print("Running one while with newvalue={},n={}".format(newvalue,n))
        if newvalue is not None:
            n=newvalue
        else:
            n-=1

c=countdown(5)
for n in c:
    print(n)
    print(n==5)
    if n==5:
        c.send(3)
        c.send(2)
