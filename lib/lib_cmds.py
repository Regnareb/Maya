import pprint, inspect, traceback
import maya.cmds as cmds


def getNumberCVs(curve):
    """Return the number of CVs of an input curve"""
    numSpans = cmds.getAttr ( curve + ".spans" )
    degree   = cmds.getAttr ( curve + ".degree" )
    form     = cmds.getAttr ( curve + ".form" )
    numCVs   = numSpans + degree
    if ( form == 2 ):
        numCVs -= degree
    return numCVs


def getTransforms(shapeList, fullPath=True):
    """Return all the transforms of the list of shapes in argument"""
    transforms = []
    for node in shapeList:
        if 'transform' != cmds.nodeType( node ):
            parent = cmds.listRelatives( node, fullPath=fullPath, parent=True )
            transforms.append( parent[0] )
    return transforms



def getTypeNode(type, nodeList):
    """ Return all the nodes of a specific type from a list of node """
    filter = cmds.itemFilter( byType=type )
    return cmds.lsThroughFilter(filter, item=nodeList)




def logException(type, value, trace):
    """ Print info on exception: sys.excepthook = logException """
    print(pprint.pformat(inspect.currentframe().f_locals))
    print(pprint.pformat(inspect.currentframe().f_builtins))
    print(pprint.pformat(inspect.currentframe().f_globals))
    print("\n\n%s"%(''.join(traceback.format_exception(type, value, trace))))
