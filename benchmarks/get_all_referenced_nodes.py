import timeit
num = 10
nodeList = cmds.ls() 

s = """
import maya.cmds as cmds
nodeList = %s
[i for i in nodeList if cmds.ls(i, rn=True)]
""" % nodeList
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
nodeList = %s
[i for i in nodeList if cmds.referenceQuery(i, isNodeReferenced=True)]
""" % nodeList
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
nodeList = %s
cmds.ls(nodeList, referencedNodes=True)
""" % nodeList
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
nodeList = %s
cmds.ls(referencedNodes=True)
""" % nodeList
print timeit.timeit(s, number=num)


# Results on huge list:
# 15.5261850357
# 10.0199069977
# 5.2493159771
# 2.59991717339

# Results on small list:
# 0.107467889786
# 0.0747890472412
# 0.0295581817627
# 2.61482691765

# equal when nodeList[0:7200] on 13911 total nodes
