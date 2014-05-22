import maya.mel as mel
import maya.cmds as cmds


def getNewNodesCreated( _function ):
    """ Return the new nodes created after the execution of a function """
    before = cmds.ls()
    eval(_function)
    after = cmds.ls()
    return list(set(after) - set(before))


def getNumberCVs( curve ):
    """Return the number of CVs of an input curve"""
    numSpans = cmds.getAttr ( curve + ".spans" )
    degree   = cmds.getAttr ( curve + ".degree" )
    form     = cmds.getAttr ( curve + ".form" )
    numCVs   = numSpans + degree
    if ( form == 2 ):
        numCVs -= degree
    return numCVs


def getNurbsCVs( surface ):
    """Return the number of CVs in U and V of the NURBS surface in argument"""
    numSpansU = cmds.getAttr ( surface + ".spansU" )
    degreeU   = cmds.getAttr ( surface + ".degreeU" )
    numSpansV = cmds.getAttr ( surface + ".spansV" )
    degreeV   = cmds.getAttr ( surface + ".degreeV" )
    formU     = cmds.getAttr ( surface + ".formU" )
    formV     = cmds.getAttr ( surface + ".formV" )
    numCVsU   = numSpansU + degreeU
    #Adjust for periodic hull:
    if ( formU == 2 ):
        numCVsU -= degreeU
    #Adjust for periodic hull:
    if ( formV != 2 ):
        numCVsV = numSpansV + degreeV

    return numCVsU, numCVsV


def getTransforms( shapeList, fullPath=True ):
    """Return all the transforms of the list of shapes in argument"""
    transforms = []
    for node in shapeList:
        if 'transform' != cmds.nodeType( node ):
            parent = cmds.listRelatives( node, fullPath=fullPath, parent=True )
            transforms.append( parent[0] )
    return transforms


def getShapes( xform ):
    """Return the shapes of a node in argument"""
    shapes = []
    if cmds.nodeType( xform ) == 'transform':
        shapes = cmds.listRelatives( xform, fullPath=True, shapes=True)
    return shapes


def getTypeNode( type, nodeList ):
    """ Return all the nodes of a specific type from a list of node """
    filter = cmds.itemFilter( byType=type )
    return cmds.lsThroughFilter(filter, item=nodeList)


def getFirstSelection( filter='' ):
    """Get the first item in the selection"""
    selection = cmds.ls(selection=True)
    if filter and selection:
        selection = cmds.filterExpand( selection, sm=filter)
    if selection:
        return selection[0]
    else:
        return ''







def undoChunk( method ):
    """A decorator that create a undo chunk so that everything done in the method will be undone with only one Undo"""
    def undoed( *args, **kw ):
        try:
            cmds.undoInfo( openChunk=True )
            result = method( *args, **kw )
        except Exception as err:
            print err
        finally:
            cmds.undoInfo( closeChunk=True )
    return undoed




class UndoContext(object):
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

# with UndoContext():
#     ... your code here....
