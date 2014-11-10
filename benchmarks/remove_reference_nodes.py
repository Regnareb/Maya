import timeit
num = 50
lis = cmds.ls() 

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
listed = cmds.ls(type='reference')
[i for i in lis if i not in listed]
""" % lis
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
lis = %s
listed = cmds.ls(type='reference')
list(set(lis) - set(listed))
""" % lis
print timeit.timeit(s, number=num)



# Results on small list:
# 1.02980017662
# 0.534548997879
# 0.28243803978
# 0.351180076599
# 0.338052988052

# Results on huge list:
# 125.933917999
# 70.3589739799
# 38.8933990002
# 2.59962010384
# 0.795596122742
