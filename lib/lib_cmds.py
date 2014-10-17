import re
import os
import time
import pickle
import maya.mel as mel
import maya.cmds as cmds
import logging
from collections import Iterable

logger = logging.getLogger(__name__)


def getNewNodesCreated(_function):
    """ Return the new nodes created after the execution of a function """
    before = cmds.ls(long=True)
    eval(_function)
    after = cmds.ls(long=True)
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


def formatPath(fileName, path='', prefix='', suffix=''):
    """ Create a complete path with a filename, a path and prefixes/suffixes
    /path/prefix_filename_suffix.ext"""
    path = os.path.join(path, "")
    if suffix:
        suffix = '_' + suffix
    if prefix:
        prefix = prefix + '_'
    fileName, fileExt = os.path.splitext(fileName)
    filePath = path + prefix + fileName + suffix + fileExt
    return filePath


def saveAsCopy(fileName='', path='', prefix='', suffix=''):
    """ Save the scene elsewhere while continuing to work on the original path """
    currentName = cmds.file(query=True, sceneName=True)
    if not fileName:
        fileName = os.path.basename(currentName)
    filePath = formatPath(fileName, path, prefix, suffix)
    cmds.file(rename=filePath)
    cmds.file(save=True)
    cmds.file(rename=currentName)
    return filePath


def export(exportList=None, fileName='', path='', prefix='', suffix=''):
    """ Export only the selection if it is passed as argument or the complete scene with references """
    if not fileName:
        fileName = os.path.basename(cmds.file(query=True, sceneName=True))
    filePath = formatPath(fileName, path, prefix, suffix)
    if exportList:
        cmds.select(exportList, noExpand=True)
    # Export references only if is on Export All mode
    cmds.file(filePath, force=True, options="v=0;", type="mayaAscii", preserveReferences=not bool(exportList), exportUnloadedReferences=not bool(exportList), exportSelected=bool(exportList), exportAll=not bool(exportList), shader=True, channels=True, constructionHistory=True, constraints=True, expressions=True)
    return filePath


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
        parent = getTransform(node)
        transforms.append(parent)
    transforms = filter(bool, transforms)
    return transforms


def getTransform(shape, fullPath=True):
    """Return the transform of the shape in argument"""
    transforms = ''
    if not isinstance(shape, basestring):
        logger.error('Input not valid. Expecting a string shape, got "%s": %s' % (type(shape).__name__, shape))
    elif 'transform' != cmds.nodeType(shape):
        transforms = cmds.listRelatives(shape, fullPath=fullPath, parent=True)
        transformd = getFirstItem(transforms, '')
    return transform


def getShapes(xform, fullPath=True):
    """Return the shapes of a node in argument"""
    shapes = []
    if cmds.nodeType(xform) == 'transform':
        shapes = cmds.listRelatives(xform, fullPath=fullPath, shapes=True)
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


def getEmptyGroups():
    """Return a list of groups with no children"""
    transforms =  cmds.ls(type='transform')
    emptyGroups = []
    for tran in transforms:
        if cmds.nodeType(tran) == 'transform':
            children = cmds.listRelatives(tran, children=True)
            if children == None:
                emptyGroups.append(tran)
    return emptyGroups


def getMaterialFromSG(shadingGroup):
    """Returns the Material node linked to the specified Shading Group node"""
    if cmds.nodeType(shadingGroup) == 'shadingEngine' and cmds.connectionInfo(shadingGroup + '.surfaceShader', isDestination=True):
        return cmds.connectionInfo(shadingGroup + '.surfaceShader', sourceFromDestination=True).split('.')[0]
    return ''


def getSGsFromShape(shape):
    """Return all the Shading Groups connected to the shape"""
    shadingEngines = cmds.listConnections(shape, destination=True, source=False, plugs=False, type="shadingEngine")
    return list(set(shadingEngines)) if shadingEngines else []


def transferMaterials(shape, toAssign):
    """Transfer materials assignation (object and faces) to a list of another objects"""
    shape = getFirstItem(getShapes(shape)) or shape
    shadingGroups = getSGsFromShape(shape)
    for sg in shadingGroups:
        assignation = cmds.sets(sg, query=True)
        assignationFinal = []
        for u in toAssign:
            if not cmds.polyCompare(shape, u):
                assignationFinal = assignationFinal + ([i.replace(transform, u) for i in assignation if transform in i])
            else:
                logger.warning('The mesh %s do not share the same topology with %s. Skipped' % (u, shape))
        cmds.sets(assignationFinal, forceElement=sg, edit=True)


def copyUV(object, toAssign):
    """Copy UVs from one mesh to a list of other objects"""
    for i in toAssign:
        if not cmds.polyCompare(object, i):
            cmds.polyTransfer(object, vertices=True, vertexColor=False, uvSets=1, alternateObject=i)
        else:
            logger.error('The mesh %s do not share the same topology with %s. Skipped' % (i, object))


def listReferences():
    """Returns a dictionary with the path to the ref, its refNode, the nodes contained in the ref, and if the ref is loaded or not"""
    references = cmds.file(query=True, reference=True)
    referencesDict = dict()
    for ref in references:
        refNode = cmds.file(ref, query=True, referenceNode=True)
        isLoaded = cmds.referenceQuery(refNode, isLoaded=True)
        nodesInRef = cmds.referenceQuery(refNode, nodes=True)
        referencesDict[ref] = [refNode, nodesInRef, isLoaded]
    return referencesDict


def unloadReferences(references=None):
    """Unload a list of references passed as argument, or every references if none is passed"""
    if not references:
        references = cmds.file(query=True, reference=True)
    for ref in references:
        if cmds.referenceQuery(ref, isLoaded=True):
            cmds.file(ref, unloadReference=True)


def loadReferences(references=None):
    """Load a list of references passed as argument, or every references if none is passed"""
    if not references:
        references = cmds.file(query=True, reference=True)
    for ref in references:
        if not cmds.referenceQuery(ref, isLoaded=True):
            cmds.file(ref, loadReference=True)


def getActiveViewport():
    """Return the active 3D viewport if any"""
    panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=panel) == 'modelPanel':
        return panel
    return ''


def getActiveCamera():
    """Return the camera of the active 3D viewport if any"""
    viewport = getActiveViewport()
    if viewport:
        return cmds.modelPanel(viewport, query=True, camera=True)
    return ''


def getCameraViewport(viewport):
    """Return the camera of a specific viewport"""
    if cmds.modelPanel(viewport, exists=True):
        return cmds.modelPanel(viewport, query=True, camera=True)
    return ''


def loadPlugin(plugin):
    cmds.loadPlugin(plugin, quiet=True)
    pluginList = cmds.pluginInfo(query=True, listPlugins=True)
    if plugin in pluginList:
        logger.info("Plugin %s correctly loaded" % plugin)
        return True
    else:
        logger.error("Couldn't load plugin: ", plugin)
        return False










def getFirstItem(iterable, default=None):
    """Return the first item if any"""
    if iterable:
        for item in iterable:
            return item
    return default


def flatten(coll):
    """Flatten a list while keeping strings"""
    for i in coll:
            if isinstance(i, Iterable) and not isinstance(i, basestring):
                for subc in flatten(i):
                    yield subc
            else:
                yield i












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



def withmany(method):
    """A decorator that iterate through all the elements and eval the """
    def many(many_foos):
        for foo in many_foos:
            yield method(foo)
    method.many = many
    return method



