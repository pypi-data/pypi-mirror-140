
def logging(func):
    def wrapper(*args, **kw):
        res = func(*args, **kw)
        print("----------------")
        print("{}():".format(func.__name__))
        print("Inputs:")
        for idx, arg in enumerate(args[1:]):
            print("\targ{} = {}".format(idx+1, arg))
        for key, val in kw.items():
            print("\t{} = {}".format(key, val))
        print("Return: \n\t{}".format(res))
        print("----------------\n\n")
        return res
    return wrapper