import timeit
num = 10

s = """
import maya.cmds as cmds
allNodes = cmds.ls()
[i for i in allNodes if cmds.referenceQuery(i, isNodeReferenced=True)]
"""
print timeit.timeit(s, number=num)

s = """
import maya.cmds as cmds
cmds.ls(referencedNodes=True)
""" 
print timeit.timeit(s, number=num)

# Results
# 11.343184948
# 2.8212761879


