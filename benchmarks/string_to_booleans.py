import timeit
num = 100000
string = 'True'

s = """
import ast
def string2bool(string):
    try:
        ast.literal_eval(string)
    except ValueError:
        return string
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    dico = {'True':True, 'False':False}
    try:
        return dico[string]
    except KeyError:
        return string
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    d = {"True":True, "False":False}
    return d.get(string, string)
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    string = False if string == 'False' else string
    string = True if string == 'True' else string
    return string
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    if string == 'False':
        return False
    elif string == 'True':
        return True
    else:
        return string
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


# Results 
# 0.746348142624
# 0.213778018951
# 0.0557010173798
# 0.0376281738281
# 0.0360729694366



# Only boolean

import timeit
num = 100000
string = 'True'

s = """
import ast
def string2bool(string):
    ast.literal_eval(string)
string2bool('%s')
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    dico = {'True':True, 'False':False}
    return dico[string]
string2bool('%s')
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    if string == 'False':
        return False
    else:
        return True
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    return False if string == 'False' else True
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


s = """
def string2bool(string):
    return string == "True"
string2bool(%s)
""" % string
print timeit.timeit(s, number=num)


# Results
# 1.19827890396
# 0.0405788421631
# 0.0305030345917
# 0.030061006546
# 0.028342962265
