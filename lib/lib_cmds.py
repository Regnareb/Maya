import maya.mel as mel
import maya.cmds as cmds


def getNewNodesCreated(_function):
    """ Return the new nodes created after the execution of a function """
    before = cmds.ls()
    eval(_function)
    after = cmds.ls()
    return list(set(after) - set(before))


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


def getShapes( xform ):
    """Return the shapes of a node in argument"""
    shapes = []
    if cmds.nodeType( xform ) == 'transform':
        shapes = cmds.listRelatives( xform, fullPath=True, shapes=True)
    return shapes


def logException(type, value, trace):
    """ Print info on exception: sys.excepthook = logException """
    print(pprint.pformat(inspect.currentframe().f_locals))
    print(pprint.pformat(inspect.currentframe().f_builtins))
    print(pprint.pformat(inspect.currentframe().f_globals))
    print("\n\n%s"%(''.join(traceback.format_exception(type, value, trace))))


def undo_chunk( method ):
    """A decorator that create a undo chunk so that everything done in the method will be undone with only one Undo"""
    def undoed( *args, **kw ):
        cmds.undoInfo( openChunk=True )
        result = method( *args, **kw )
        cmds.undoInfo( closeChunk=True )
    return undoed
    
    
    
