import re
import os
import time
import errno
import pickle
import logging
from collections import Iterable
import maya.mel as mel
import maya.cmds as cmds
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

def normpath(path):
    """Fix some problems with Maya evals or some file commands needing double escaled anti-slash '\\\\' in the path in Windows"""
    return os.path.normpath(path).replace('\\', '/')

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


def export(exportList=None, fileName='', path='', prefix='', suffix='', format=''):
    """ Export only the selection if it is passed as argument or the complete scene with references"""
    if not fileName:
        fileName = os.path.basename(cmds.file(query=True, sceneName=True)) or 'nosave'
    filePath = formatPath(fileName, path, prefix, suffix)
    if exportList:
        cmds.select(exportList, noExpand=True)
    if not format:
        format = getFirstItem(cmds.file(type=True, query=True)) or 'mayaAscii'
    # Export references only if is on Export All mode
    finalPath = cmds.file(filePath, force=True, options="v=0;", type=format, preserveReferences=not bool(exportList), exportUnloadedReferences=not bool(exportList), exportSelected=bool(exportList), exportAll=not bool(exportList), shader=True, channels=True, constructionHistory=True, constraints=True, expressions=True)
    return finalPath


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

def getUDIM(shapes):
    shapesUV = cmds.polyListComponentConversion(shapes, fromFace=True, toUV=True)
    uvCoord = cmds.polyEditUV(shapesUV, q=True)
    Umin = int(min(uvCoord[0::2]))
    Vmin = int(min(uvCoord[1::2]))
    return [Umin, Vmin]



def getTransform(shape, fullPath=True):
    """Return the transform of the shape in argument"""
    transforms = ''
    if not isinstance(shape, basestring):
        logger.error('Input not valid. Expecting a string shape, got "%s": %s' % (type(shape).__name__, shape))
    elif 'transform' != cmds.nodeType(shape):
        transforms = cmds.listRelatives(shape, fullPath=fullPath, parent=True)
        transform = getFirstItem(transforms, '')
    return transform


def getTransforms(shapeList, fullPath=True):
    """Return all the transforms of the list of shapes in argument"""
    transforms = []
    for node in shapeList:
        parent = getTransform(node, fullPath)
        transforms.append(parent)
    transforms = filter(bool, transforms)
    return transforms


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
    return getFirstItem(selection, '')


def isVisible(node):
    visible = False
    try:
        visible = cmds.getAttr(node + '.visibility')
        visible = visible and not cmds.getAttr(node + '.intermediateObject')
    except ValueError:
        pass
    try:
        visible = visible and cmds.getAttr(node + '.overrideVisibility')
    except ValueError:
        pass
    if visible:
        parents = cmds.listRelatives(node, parent=True)
        if parents:
            visible = isVisible(getFirstItem(parents))
    return visible


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
        return cmds.connectionInfo(shadingGroup + '.surfaceShader', sourceFromDestination=True).split('.')[0] # Faster than cmds.listConnections(shader, type="lambert")
    return ''


def getSGsFromMaterial(shader):
    if cmds.ls(shader, materials=True):
        nodes = [i.split('.')[0] for i in cmds.connectionInfo(shader +'.outColor', destinationFromSource=True)]  # Faster than cmds.listConnections(shader, type="shadingEngine")
        shadingGroups = [i for i in nodes if cmds.nodeType(i) == 'shadingEngine']
        return shadingGroups
    return []


def getSGsFromShape(shape):
    """Return all the Shading Groups connected to the shape"""
    shadingEngines = cmds.listSets(object=shape, type=1, extendToShape=True) # Faster than cmds.listConnections(shape, destination=True, source=False, plugs=False, type="shadingEngine")
    return list(set(shadingEngines)) if shadingEngines else []


def getShaderAssignation(shader):
    shadingGroups = getSGsFromMaterial(shader) # Add checks?
    if shadingGroups:
        return cmds.sets(shadingGroups, query=True) or []
    return []


def transferMaterials(shape, toAssign, worldSpace=True):
    """Transfer materials assignation (object and faces) to a list of another objects"""
    for mesh in toAssign:
        cmds.transferShadingSets(shape, mesh, sampleSpace=worldSpace)


def copyUV(object, toAssign):
    """Copy UVs from one mesh to a list of other objects"""
    for i in toAssign:
        if not cmds.polyCompare(object, i):
            cmds.polyTransfer(object, vertices=True, vertexColor=False, uvSets=1, alternateObject=i)
        else:
            logger.error('The mesh %s do not share the same topology with %s. Skipped' % (i, object))



def getReferences(loadState=False, nodesInRef=False):
    """Returns a dictionary with the namespace as keys
    and a list containing the proxyManager if there is one, the refnode, and its load state
    """
    result = dict()
    proxyManagers = set()
    references = cmds.file(query=True, reference=True)
    for i in references:
        refNode = cmds.referenceQuery(i, referenceNode=True)
        connection = cmds.connectionInfo(refNode + '.proxyMsg', sourceFromDestination=True)
        if connection:
            proxyManagers.update([connection.split('.')[0]])
        else:
            namespace = cmds.file(i, parentNamespace=True, query=True)[0] + ':' + cmds.file(i, namespace=True, query=True)
            namespace =  cmds.file(i, namespace=True, query=True)
            # namespace = ('' if namespace.startswith(':') else ':') + namespace
            result[namespace] = {'proxyManager': None, 'refNode': refNode}

    for proxy in proxyManagers:
        connection = cmds.connectionInfo(proxy + '.activeProxy', destinationFromSource=True)
        activeProxy = cmds.listConnections(connection, source=False)[0]
        namespace = cmds.referenceQuery(activeProxy, parentNamespace=True)[0]
        refNode = cmds.referenceQuery(activeProxy, referenceNode=True)
        result[namespace] = {'proxyManager': proxy, 'refNode': refNode}

    for ref in result:
        if loadState:
            isLoaded = cmds.referenceQuery(result[ref]['refNode'], isLoaded=True)
            result[ref]['isLoaded'] = isLoaded
        if nodesInRef:
            nodes = cmds.referenceQuery(result[ref]['refNode'], nodes=True)
            result[ref]['nodesInRef'] = nodes
    return result


def getReferences2():
    """Returns a dictionary with the namespace as keys
    and a list containing the proxyManager if there is one, the refnode, and its load state
    """
    result = dict()
    proxyRefs = []
    references = cmds.ls(references=True)
    for i in cmds.ls(type='proxyManager'):
        proxyRefs += cmds.listConnections(i + '.proxyList', source=False)
        connection = cmds.connectionInfo(i + '.activeProxy', destinationFromSource=True)
        activeProxy = cmds.listConnections(connection, source=False)[0]
        namespace = cmds.referenceQuery(activeProxy, namespace=True)
        isLoaded = cmds.referenceQuery(activeProxy, isLoaded=True)
        result[namespace] = [i, activeProxy, isLoaded]

    for i in proxyRefs:
        references.remove(i)
    for i in references:
        try:
            refNode = cmds.referenceQuery(i, referenceNode=True, topReference=True)
            namespace = cmds.referenceQuery(activeProxy, namespace=True)
            isLoaded = cmds.referenceQuery(i, isLoaded=True)
            result[namespace] = [None, refNode, isLoaded]
        except RuntimeError, e:
            logger.error(e)
    return result


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
    """Load the plugin specified in argument"""
    plugMethod = {'Mayatomr': loadMayatomr, 'Turtle': loadTurtle}
    if plugin in plugMethod:
        plugMethod[plugin]()
    else:
        cmds.loadPlugin(plugin, quiet=True)
    pluginList = cmds.pluginInfo(query=True, listPlugins=True)
    if plugin in pluginList:
        logger.info("Plugin %s correctly loaded" % plugin)
        return True
    else:
        logger.error("Couldn't load plugin: " % plugin)
        return False


def loadMayatomr():
    """Unlock the nodes, load MentalRay, then relock the nodes to avoid a bad initialisation"""
    lockedNodes = cmds.ls(lockedNodes=True)
    toRemove = cmds.ls(referencedNodes=True) + cmds.ls(type='reference')
    lockedNodes = list(set(lockedNodes) - set(toRemove))
    try:
        if lockedNodes:
            cmds.lockNode(lockedNodes, lock=False)
        cmds.loadPlugin('Mayatomr', quiet=True)
        if lockedNodes:
            cmds.lockNode(lockedNodes, lock=True)
        return True
    except RuntimeError, e:
        logger.error(e)
        return False


def loadTurtle():
    cmds.loadPlugin('Turtle', quiet=True)
    turtleNodes = {'ilrUIOptionsNode': 'TurtleUIOptions',
                   'ilrBakeLayerManager': 'TurtleBakeLayerManager',
                   'ilrBakeLayer': 'TurtleDefaultBakeLayer',
                   'ilrOptionsNode': 'TurtleRenderOptions'}
    for nodeType, nodeName in turtleNodes.iteritems():
        if not cmds.objExists(nodeName):
            cmds.createNode(nodeType, name=nodeName)


def createFileNode(name='file'):
    texture = cmds.shadingNode('file', asTexture=True)
    placement = cmds.shadingNode('place2dTexture', asUtility=True)
    attributes = ['.coverage', '.translateFrame', '.rotateFrame', '.mirrorU', '.mirrorV', '.stagger', '.wrapU', '.wrapV', '.repeatUV', '.offset', '.rotateUV', '.noiseUV', '.vertexUvOne', '.vertexUvTwo', '.vertexUvThree', '.vertexCameraOne']
    for attr in attributes:
        cmds.connectAttr(placement + attr, texture + attr, force=True)
    cmds.connectAttr(placement + '.outUV', texture + '.uv', force=True)
    cmds.connectAttr(placement + '.outUvFilterSize', texture + '.uvFilterSize', force=True)
    return texture, placement


def deleteUnknownPluginNodes(plugin):
    """Delete nodes related to a specific unknown plugin
    Maya 2015 SP6 and up only
    """
    unknownNodes = cmds.ls(type='unknown')
    for node in unknownNodes:
        plug = cmds.unknownNode(node, query=True, plugin=True)
        if plug == plugin:
            cmds.lockNode(node, lock=0)
            cmds.delete(node)
            logger.debug('Deleted node: {0}'.format(node))


def deleteUnknownPlugins():
    """Delete all and unknown plugins referenced and their related nodes
    Maya 2015 SP6 and up only!
    """
    unknownPlugins = cmds.unknownPlugin(query=True, list=True) or []
    for plugin in unknownPlugins:
        deleteUnknownPluginNodes(plugin)
        cmds.unknownPlugin(plugin, remove=True)
        logger.debug('Removed the plugin: {0}'.format(plugin))


def setAllPanelsToRenderer(renderer, reset=True):
    """Set all the models panels to the specified renderer. It will do a reset of everything regarding the Viewport 2.0 if no model panels use it.
    Possible values: base_OpenGL_Renderer, hwRender_OpenGL_Renderer, vp2Renderer
    """
    modelPanels = cmds.getPanel(type='modelPanel')
    for panel in modelPanels:
        cmds.modelEditor(panel, edit=True, rendererName=renderer)
    if reset or os.environ.get('MAYA_DISABLE_VP2_WHEN_POSSIBLE', False):
        cmds.ogs(reset=True)












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

def string2bool(string, strict=True):
    """Convert a string to its boolean value.
    The strict argument keep the string if neither True/False are found
    """
    if strict:
        return string == "True"
    else:
        if string == 'True':
            return False
        elif string == 'False':
            return True
        else:
            return string

def createDir(path):
    """Creates a directory"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def camelCaseSeparator(label, separator=' '):
    """Convert a CamelCase to words separated by separator"""
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r'%s\1' % separator, label)

def toNumber(s):
    """Convert a string to an int or a float depending of their types"""
    try:
        return int(s)
    except ValueError:
        return float(s)

def replaceExtension(path, ext):
    if ext and not ext.startswith('.'):
        ext = ''.join(['.', ext])
    return path.replace(os.path.splitext(path)[1], ext)

def humansize(nbytes):
    suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def lstripAll(toStrip, stripper):
    if toStrip.startswith(stripper):
        return toStrip[len(stripper):]
    return toStrip

def rstripAll(toStrip, stripper):
    if toStrip.endswith(stripper):
        return toStrip[:-len(stripper)]
    return toStrip











def reSelect(method):
    """A decorator that reselect the elements selected prior the execution of the method"""
    def selected(*args, **kw):
        sel = cmds.ls(sl=True)
        result = method(*args, **kw)
        if sel:
            cmds.select(sel)
    return selected


class ReselectContext(object):
    def __enter__(self):
        self.selectionList = cmds.ls(sl=True)
    def __exit__(self, *exc_info):
        if self.selectionList:
            cmds.select(self.selectionList)

# with ReselectContext():
#     ... your code here....


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
    """A decorator that iterate through all the elements and eval each one if a list is in input"""
    def many(many_foos):
        for foo in many_foos:
            yield method(foo)
    method.many = many
    return method


def memoizeSingle(f):
    """Memoization decorator for a function taking a single argument"""
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


def memoizeSeveral(f):
    """Memoization decorator for functions taking one or more arguments"""
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)
