import timeit
num = 50
lis = cmds.ls() 


# cmds.findType(lis, type='reference')
# Forget about it


s = """
import maya.cmds as cmds
lis = %s
[i for i in lis if not cmds.ls(i, type='reference')]
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
[i for i in lis if not cmds.objectType(i, isType='reference')]
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
[i for i in lis if cmds.nodeType(i) != 'reference']
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
toRemove = cmds.ls(lis, type='reference')
[i for i in lis if i not in toRemove]
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
toRemove = cmds.ls(lis, type='reference')
list(set(lis) - set(toRemove))
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
toRemove = cmds.ls(type='reference')
[i for i in lis if i not in toRemove]
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
toRemove = cmds.ls(type='reference')
list(set(lis) - set(toRemove))
""" % lis
print timeit.timeit(s, number=num)


# Results on small list:
# 1.03518795967
# 0.559606075287
# 0.295418977737
# 0.110281944275
# 0.0975658893585
# 0.45898103714
# 0.444609880447

# Results on huge list:
# 126.594508886
# 73.218061924
# 41.0703258514
# 16.4379661083
# 14.49990201
# 2.75426411629
# 0.860762119293
