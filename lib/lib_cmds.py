import re
import time
import pickle
import maya.mel as mel
import maya.cmds as cmds


def getNewNodesCreated(_function):
    """ Return the new nodes created after the execution of a function """
    before = cmds.ls()
    eval(_function)
    after = cmds.ls()
    return list(set(after) - set(before))


def pickleObject(fullPath, toPickle):
    """ Pickle an object at the designated path """
    with open(fullPath, 'w') as f:
        pickle.dump(toPickle, f)
    f.close()


def unPickleObject(fullPath):
    """ unPickle an object from the designated file path """
    with open(fullPath, 'r') as f:
        fromPickle = pickle.load(f)
    f.close()
    return fromPickle


def getShaders(listMeshes):
    """Return a list of shaders assigned to the list of shapes/transforms passed in argument"""
    shadingGrps = cmds.listConnections(listMeshes, type='shadingEngine')
    return cmds.ls(cmds.listConnections(shadingGrps), materials=1)


def stripShaderName(name):
    """ Return only the name of the shader """
    return re.search("_(.*?)_", name).group(0).strip('_')


def saveAsCopy(prefix='', suffix='', path='/tmp/'):
    """ Save the scene elsewhere while continuing to work on the original path """
    if suffix:
        suffix = '_' + suffix
    if prefix:
        prefix = prefix + '_'
    currentName = cmds.file(query=True, sceneName=True)
    fileName = os.path.basename(cmds.file(query=True, sceneName=True))
    fileName, fileExt = os.path.splitext(fileName)
    tmpPath = path + prefix + fileName + suffix + fileExt
    cmds.file(rename=tmpPath)
    cmds.file(save=True)
    cmds.file(rename=currentName)
    return tmpPath


def getNumberCVs(curve):
    """Return the number of CVs of an input curve"""
    numSpans = cmds.getAttr (curve + ".spans")
    degree   = cmds.getAttr (curve + ".degree")
    form     = cmds.getAttr (curve + ".form")
    numCVs   = numSpans + degree
    if (form == 2):
        numCVs -= degree
    return numCVs


def getNurbsCVs(surface):
    """Return the number of CVs in U and V of the NURBS surface in argument"""
    numSpansU = cmds.getAttr(surface + ".spansU")
    degreeU   = cmds.getAttr(surface + ".degreeU")
    numSpansV = cmds.getAttr(surface + ".spansV")
    degreeV   = cmds.getAttr(surface + ".degreeV")
    formU     = cmds.getAttr(surface + ".formU")
    formV     = cmds.getAttr(surface + ".formV")
    numCVsU   = numSpansU + degreeU
    #Adjust for periodic hull:
    if formU == 2:
        numCVsU -= degreeU
    numCVsV   = numSpansV + degreeV
    #Adjust for periodic hull:
    if formV == 2:
        numCVsV -= degreeV

    return numCVsU, numCVsV


def getTransforms(shapeList, fullPath=True):
    """Return all the transforms of the list of shapes in argument"""
    transforms = []
    for node in shapeList:
        if 'transform' != cmds.nodeType(node):
            parent = cmds.listRelatives(node, fullPath=fullPath, parent=True)
            transforms.append(parent[0])
    return transforms


def getShapes(xform):
    """Return the shapes of a node in argument"""
    shapes = []
    if cmds.nodeType(xform) == 'transform':
        shapes = cmds.listRelatives(xform, fullPath=True, shapes=True)
    return shapes


def getTypeNode(nodeType, nodeList):
    """ Return all the nodes of a specific type from a list of node """
    filterName = cmds.itemFilter(byType=nodeType)
    return cmds.lsThroughFilter(filterName, item=nodeList)


def getFirstSelection(filterNb=None, longName=False):
    """Get the first item in the selection"""
    selection = cmds.ls(selection=True, long=longName)
    if filterNb and selection:
        selection = cmds.filterExpand(selection, sm=filterNb)
    if selection:
        return selection[0]
    else:
        return ''


def longNameOf(node):
    """Return the full path of a node"""
    return cmds.ls(node, long=True)[0]


def shortNameOf(node):
    """Return the short name of a node"""
    return node.split('|')[-1]


def createGroupHierarchy(path):
    """Create a succession of empty transforms if they do not exist"""
    tmpPath = ''
    for i in path.strip('|').split('|'):
        if cmds.objExists(tmpPath + '|' + i):
            pass
        else:
            group = cmds.group(empty=True, name=i)
            if tmpPath:
                cmds.parent(group, tmpPath)
        tmpPath = tmpPath + '|' + i










def reSelect(method):
    """A decorator that reselect the elements selected prior the execution of the method"""
    def selected(*args, **kw):
        sel = cmds.ls(sl=True)
        result = method(*args, **kw)
        cmds.select(sel)
    return selected


class ReselectContext(object):
    def __enter__(self):
        self.selectionList = cmds.ls(sl=True)
    def __exit__(self, *exc_info):
        cmds.select(self.selectionList)



def undoChunk(method):
    """A decorator that create a undo chunk so that everything done in the method will be undone with only one Undo"""
    def undoed(*args, **kw):
        try:
            cmds.undoInfo(openChunk=True)
            result = method(*args, **kw)
        except Exception as err:
            print err
        finally:
            cmds.undoInfo(closeChunk=True)
    return undoed


class UndoContext(object):
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

# with UndoContext():
#     ... your code here....
