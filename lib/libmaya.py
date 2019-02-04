import os
import re
import time
import logging
import functools
import contextlib
import maya.mel as mel
import maya.cmds as cmds
import libpython
logger = logging.getLogger(__name__)


# cmds.ls([None, 'bla'], type='TrucType') # BUG
# pymel.core.open('', force=True)
# cmds.getAttr('node.attribute')  # If several nodes have the same name, it will return a list instead of only one element or  crashing



def getNewNodesCreated(_function):
    """ Return the new nodes created after the execution of a function """
    before = cmds.ls(long=True)
    eval(_function)
    after = cmds.ls(long=True)
    return list(set(after) - set(before))


def getShaders(listMeshes):
    """Return a list of shaders assigned to the list of shapes/transforms passed in argument"""
    shadingGrps = cmds.listConnections(listMeshes, type='shadingEngine')
    return cmds.ls(cmds.listConnections(shadingGrps), materials=1)


def saveAsCopy(path):
    """ Save the scene elsewhere while continuing to work on the original path """
    currentname = cmds.file(query=True, sceneName=True)
    head, tail = os.path.split(currentname)
    folder, filename = os.path.split(path)
    if not folder:
        folder = head
    if not filename:
        filename = tail + '_Copy'
    filepath = libpython.normpath(os.path.join(folder, filename))
    cmds.file(rename=filepath)
    cmds.file(save=True)
    cmds.file(rename=currentname)
    return filepath


def export(exportList=None, fileName='', path='', prefix='', suffix='', format=''):
    """ Export only the selection if it is passed as argument or the complete scene with references"""
    if not fileName:
        fileName = os.path.basename(cmds.file(query=True, sceneName=True)) or 'nosave'
    filePath = libpython.formatPath(fileName, path, prefix, suffix)
    if exportList:
        cmds.select(exportList, noExpand=True)
    if not format:
        format = libpython.getFirstItem(cmds.file(type=True, query=True)) or 'mayaAscii'
    # Export references only if is on Export All mode
    finalPath = cmds.file(filePath, force=True, options="v=0;", type=format, preserveReferences=not bool(exportList), exportUnloadedReferences=not bool(exportList), exportSelected=bool(exportList), exportAll=not bool(exportList), shader=True, channels=True, constructionHistory=True, constraints=True, expressions=True)
    return finalPath


def getNumberCVs(curve):
    """Return the number of CVs of an input curve"""
    numSpans = cmds.getAttr(curve + ".spans")
    degree = cmds.getAttr(curve + ".degree")
    form = cmds.getAttr(curve + ".form")
    numCVs = numSpans + degree
    if (form == 2):
        numCVs -= degree
    return numCVs


def getNurbsCVs(surface):
    """Return the number of CVs in U and V of the NURBS surface in argument"""
    numSpansU = cmds.getAttr(surface + ".spansU")
    degreeU = cmds.getAttr(surface + ".degreeU")
    numSpansV = cmds.getAttr(surface + ".spansV")
    degreeV = cmds.getAttr(surface + ".degreeV")
    formU = cmds.getAttr(surface + ".formU")
    formV = cmds.getAttr(surface + ".formV")
    numCVsU = numSpansU + degreeU
    # Adjust for periodic hull:
    if formU == 2:
        numCVsU -= degreeU
    numCVsV = numSpansV + degreeV
    # Adjust for periodic hull:
    if formV == 2:
        numCVsV -= degreeV
    return numCVsU, numCVsV


def getUDIM(shapes):
    shapesUV = cmds.polyListComponentConversion(shapes, fromFace=True, toUV=True)
    uvCoord = cmds.polyEditUV(shapesUV, q=True)
    Umin = int(min(uvCoord[0::2]))
    Vmin = int(min(uvCoord[1::2]))
    return [Umin, Vmin]


def uvToUdim(uv):
    neg = -10 if uv[1] < 0 else 0
    return int(1000 + (int(uv[1]) * 10) + (uv[0] + 1)) + neg


def getTransform(shape, fullPath=True):
    """Return the transform of the shape in argument"""
    transforms = ''
    if not isinstance(shape, basestring):
        logger.error('Input not valid. Expecting a string shape, got "%s": %s' % (type(shape).__name__, shape))
    elif 'transform' != cmds.nodeType(shape):
        transforms = cmds.listRelatives(shape, fullPath=fullPath, parent=True)
        transform = libpython.getFirstItem(transforms, '')
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
    filterName = cmds.itemFilter(byType=nodeType, uniqueNodeNames=True)
    result = cmds.lsThroughFilter(nodeList, item=filterName)
    return result


def getFirstSelection(filterNb=None, longName=False):
    """Get the first item in the selection"""
    selection = cmds.ls(selection=True, long=longName)
    if filterNb and selection:
        selection = cmds.filterExpand(selection, sm=filterNb)
    return libpython.getFirstItem(selection, '')


def getNextFreeMultiIndex(nodeattr, start=0, max=10000000):
    """Get the next available index, usefull for indexMatters(True) nodes like the plusMinusAverage."""
    for i in xrange(start, max):
        con = cmds.connectionInfo(nodeattr + "[{}]".format(i), sourceFromDestination=True)
        if not con:
            return i
    return None


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
        parents = cmds.listRelatives(node, parent=True, path=True)
        if parents:
            visible = isVisible(libpython.getFirstItem(parents))
    return visible


def longNameOf(node):
    """Return the full path of a node"""
    return cmds.ls(node, long=True)[0]


def shortNameOf(node):
    """Return the short name of a node"""
    return node.split('|')[-1]


def renameDuplicateNodes(nodes):
    for node in nodes:
        new = node
        while cmds.objExists(new):
            new = libpython.incrementString(shortNameOf(new))
        cmds.rename(node, new)


def multiParentConstraint(nodes=None, maintainOffset=True, weight=1, skipTranslate=[], skipRotate=[]):
    if nodes is None:
        nodes = cmds.ls(sl=True)
    source = nodes.pop()
    cmds.select(clear=True)
    result = {}
    for node in nodes:
       result[node] = cmds.parentConstraint(source, node, maintainOffset=maintainOffset, weight=weight, skipTranslate=skipTranslate, skipRotate=skipRotate)
    return result


def createGroupHierarchy(path):
    """Create a succession of empty transforms if they do not exist"""
    tmpPath = ''
    for i in path.strip('|').split('|'):
        if cmds.objExists(tmpPath + '|' + i):
            pass
        else:
            group = cmds.group(empty=True, name=i)
            if tmpPath:
                parented = cmds.parent(group, tmpPath)
                cmds.rename(parented, i)
        tmpPath = tmpPath + '|' + i


def isGroup(node):
    if cmds.nodeType(node) != 'transform':
        return False
    childrens = cmds.listRelatives(node, children=True, path=True) or []
    for child in childrens:
        if cmds.nodeType(child) != 'transform':
            return False
    return True


def getEmptyGroups():
    """Return a list of groups with no children"""
    transforms = cmds.ls(type='transform')
    emptyGroups = []
    for tran in transforms:
        if cmds.nodeType(tran) == 'transform':
            children = cmds.listRelatives(tran, children=True)
            if children is None:
                emptyGroups.append(tran)
    return emptyGroups


def getAllAscendantConnections(nodes):
    ancestors = set()
    while nodes:
        ancestors.update(nodes)
        parents = cmds.listConnections(nodes, source=False)
        nodes = list(set(parents) - ancestors)
    return list(ancestors)


def getReferencesConnections(refNodes=[]):
    result = {}
    refs = getReferences(nodesInRef=True)
    for i in refs.values():
        if refNodes and i['refNode'] not in refNodes:
            continue
        curves = cmds.ls(i['nodesInRef'], type='nurbsCurve', long=True)
        curves = getTransforms(curves)
        try:
            parents = getAllAscendantConnections(curves)
            parents = cmds.ls(parents, type='transform', long=True)
            parents = [u for u in parents if cmds.referenceQuery(u, isNodeReferenced=True)]
            for parent in parents:
                if i['refNode'] != cmds.referenceQuery(parent, referenceNode=True):
                    result.setdefault(i['refNode'], set()).add(cmds.referenceQuery(parent, referenceNode=True))
        except TypeError:
            pass
    for i in result:
        result[i] = list(result[i])

    return result


def getMaterialFromSG(shadingGroup):
    """Returns the Material node linked to the specified Shading Group node"""
    if cmds.nodeType(shadingGroup) == 'shadingEngine' and cmds.connectionInfo(shadingGroup + '.surfaceShader', isDestination=True):
        return cmds.connectionInfo(shadingGroup + '.surfaceShader', sourceFromDestination=True).split('.')[0]  # Faster than cmds.listConnections(shader, type="lambert")
    return ''


def getSGsFromMaterial(shader):
    if cmds.ls(shader, materials=True):
        nodes = [i.split('.')[0] for i in cmds.connectionInfo(shader + '.outColor', destinationFromSource=True)]  # Faster than cmds.listConnections(shader, type="shadingEngine")
        shadingGroups = [i for i in nodes if cmds.nodeType(i) == 'shadingEngine']
        return shadingGroups
    return []


def getSGsFromShape(shape):
    """Return all the Shading Groups connected to the shape"""
    shadingEngines = cmds.listSets(object=shape, type=1, extendToShape=True)  # Faster than cmds.listConnections(shape, destination=True, source=False, plugs=False, type="shadingEngine")
    return list(set(shadingEngines)) if shadingEngines else []


def getShaderAssignation(shader):
    shadingGroups = getSGsFromMaterial(shader)  # Add checks?
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
            namespace = cmds.file(i, namespace=True, query=True)
            # namespace = ('' if namespace.startswith(':') else ':') + namespace
            result[i] = {'namespace': namespace, 'proxyManager': None, 'refNode': refNode}

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
            nodes = cmds.referenceQuery(result[ref]['refNode'], nodes=True, dagPath=True)
            result[ref]['nodesInRef'] = nodes
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


def renameReference(reference, name):
    cmds.file(reference, edit=True, namespace=name)
    refNode = cmds.file(reference, query=True, referenceNode=True)
    cmds.lockNode(refNode, lock=False)
    result = cmds.rename(refNode, name + 'RN')
    cmds.lockNode(result, lock=True)
    return result


def unloadReferences(references=[]):
    """Unload a list of references passed as argument, or every references if none is passed"""
    if not references:
        references = cmds.file(reference=True, loadReferenceDepth='none')
    for ref in references:
        if cmds.referenceQuery(ref, isLoaded=True):
            cmds.file(ref, unloadReference=True)


def loadReferences(references=[]):
    """Load a list of references passed as argument, or every references if none is passed"""
    if not references:
        references = cmds.file(reference=True, loadReferenceDepth='all')
    for ref in references:
        if not cmds.referenceQuery(ref, isLoaded=True):
            cmds.file(ref, loadReference=True)


def removeReferences(references=[]):
    for ref in references:
        cmds.file(ref, removeReference=True)


def getIncrementedNamespace(namespace, separator='', padding=None, start=None):
    regex = '^(.+?){}(\d*)$'.format(re.escape(separator) + '*' if separator else separator)
    match = re.match(regex, namespace)
    base, nb = match.groups()
    if padding is None:
        padding = len(nb)  # use the initial padding if none is specified in argument
    if start is not None:
        nb = start  # force the increment to start at a specific number
    f = '{}{{:0>{}d}}'.format(separator, padding)
    namespace = base + f.format(int(nb or 1))
    namespaces = [i['namespace'] for i in getReferences().values()]
    while namespace in namespaces:
        match = re.match(regex, namespace)
        base, nb = match.groups()
        namespace = base + f.format(int(nb) + 1)
    return namespace


def checkReferences(padding=3):
    tofix = {}
    for key, val in getReferences().iteritems():
        if re.search('RN\d$', val['refNode']):
            tofix[key] = val
        elif libpython.rstripAll(val['refNode'], 'RN') != val['namespace']:
            tofix[key] = val
        elif padding and not re.search(r'_\d{{{}}}$'.format(padding), val['namespace']):
            tofix[key] = val
        elif padding and not re.search(r'_\d{{{}}}RN$'.format(padding), val['refNode']):
            tofix[key] = val
    return tofix


def fixReferences(padding=3, start=None):
    """Rename namespaces and refnodes accordingly if there is a refnode named RN1/RN2/etc. or if the number of digits in the padding is incorrect, either in namespace or refnode name.
    Several references share the same namespace and could bring some bugs. Rename with the next incremented number available.
    """
    tofix = checkReferences(padding)
    f = None
    for f, values in tofix.iteritems():
        incremented = getIncrementedNamespace(values['namespace'], separator='_', padding=padding, start=start)
        renameReference(f, incremented)
    if f:
        fixReferences(padding=padding, start=start)
    return getReferences()


def fixDoubleNamespaces():
    """Import all elements into existing hierarchy if it already exists. Then delete the namespace and fixReferences()"""
    namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True, fullName=True)
    namespacesTofix = list(set([i.split(':')[0] for i in namespaces if ':' in i]))  # Fix double namespaces

    for namespace in namespacesTofix:
        content = cmds.namespaceInfo(namespace, listNamespace=True, dagPath=True)
        tofixList = [i for i in content if cmds.ls(i.replace(namespace + ':', ''))]  # Check if nodes already exists with the same name if we remove the namespace

        tofix = {}
        for i in tofixList:  # Sort the elements by hierarchy level
            lenght = len(i.split('|'))
            try:
                tofix[lenght].append(i)
            except KeyError:
                tofix[lenght] = [i]

        for keys, values in reversed(sorted(tofix.iteritems())):
            for node in values:
                if isGroup(node):
                    childrens = cmds.listRelatives(node, children=True, fullPath=True) or []
                    for u in childrens:
                        upperGrp = node.replace(namespace + ':', '')
                        cmds.parent(u, upperGrp)  # parent each child to the original group
                    cmds.delete(node)  # then delete the empty group

        fixReferences()
        cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
    return namespacesTofix


def getNestedNamespaces(levels, strict=False):
    namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True, fullName=True)
    result = []
    for namespace in namespaces:
        if strict and namespace.count(':') == levels:
            result.append(namespace)
        elif not strict and namespace.count(':') >= levels:
            result.append(namespace)
    return result


def getActiveViewport():
    """Return the active 3D viewport if any"""
    panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=panel) == 'modelPanel':
        return panel
    return ''


def getActiveCamera():
    """Return the camera of the active 3D viewport if any"""
    return cmds.lookThru(query=True)


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
    pluginList = cmds.pluginInfo(query=True, listPlugins=True) or []
    if plugin in pluginList:
        logger.info("Plugin {} correctly loaded".format(plugin))
        return True
    else:
        logger.error("Couldn't load plugin: {}".format(plugin))
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
    """Turtle fail to load if loaded by script, this fixes it by creating the nodes and connexions."""
    cmds.loadPlugin('Turtle', quiet=True)
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "turtle", type="string")
    turtleNodes = {'ilrUIOptionsNode': 'TurtleUIOptions',
                   'ilrBakeLayerManager': 'TurtleBakeLayerManager',
                   'ilrBakeLayer': 'TurtleDefaultBakeLayer',
                   'ilrOptionsNode': 'TurtleRenderOptions'}
    for nodeType, nodeName in turtleNodes.iteritems():
        if not cmds.objExists(nodeName) or nodeType != cmds.nodeType(nodeName):
            turtleNodes[nodeType] = cmds.createNode(nodeType, name=nodeName)
    try:
        cmds.connectAttr(turtleNodes['ilrOptionsNode']+'.message', turtleNodes['ilrBakeLayer']+'.renderOptions')
        cmds.connectAttr(turtleNodes['ilrBakeLayer']+'.index', turtleNodes['ilrBakeLayerManager']+'.bakeLayerId[0]')
    except RuntimeError:
        logger.debug('Turtle nodes already connected.')
        
    return turtleNodes


def checkPlugins(plugins):
    """Check if plugin are loaded."""
    pluginList = cmds.pluginInfo(query=True, listPlugins=True) or []
    for plugin in plugins:
        if plugin not in pluginList:
            loadPlugin(plugin)
    pluginList = cmds.pluginInfo(query=True, listPlugins=True) or []
    notloaded = [i for i in plugins if i not in pluginList]
    if notloaded:
        raise RuntimeError("Some plugins won't load: {}".format(', '.join(notloaded)))


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
    modelPanels = cmds.getPanel(type='modelPanel') or []
    for panel in modelPanels:
        cmds.modelEditor(panel, edit=True, rendererName=renderer)
    if reset or os.environ.get('MAYA_DISABLE_VP2_WHEN_POSSIBLE', False):
        cmds.ogs(reset=True)


def temporise(seconds=30):
    """Try to let Maya initialise its viewport, to let the assembly load
    by playing the current frame for the number of seconds passed as arguments."""
    start = time.time()
    elapsed = 0
    current = cmds.currentTime(query=True)
    while elapsed <= seconds:
        cmds.currentTime(current)
        elapsed = time.time() - start


def quitMayapy(status):
    """ Quit mayapy so that it can return an exitcode 0 without crashing."""
    cmds.file(new=True, force=True)
    os._exit(status)


def getMayaGlobals(variable):
    return mel.eval('$dummy = ${}'.format(variable))







def reSelect(method):
    """A decorator that reselect the elements selected prior the execution of the method"""
    @functools.wraps(method)
    def selected(*args, **kw):
        sel = cmds.ls(sl=True)
        result = method(*args, **kw)
        if sel:
            cmds.select(sel)
        return result
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
    @functools.wraps(method)
    def undoed(*args, **kw):
        err = None
        try:
            cmds.undoInfo(openChunk=True)
            result = method(*args, **kw)
        except Exception as err:
            pass
        finally:
            cmds.undoInfo(closeChunk=True)
        if err:
            raise err
        return result
    return undoed


class UndoContext(object):

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

# with UndoContext():
#     ... your code here....


def keepNamespace(method):
    """A decorator that reselect the elements selected prior the execution of the method"""
    @functools.wraps(method)
    def namespace(*args, **kw):
        np = cmds.namespaceInfo(currentNamespace=True)
        result = method(*args, **kw)
        cmds.namespace(set=np)
        return result
    return namespace


def keepTimeline(method):
    """A decorator that keep the timeline settings - min/max/submin/submax"""
    @functools.wraps(method)
    def namespace(*args, **kw):
        minTime = cmds.playbackOptions(minTime=True, query=True)
        maxTime = cmds.playbackOptions(maxTime=True, query=True)
        animationStartTime = cmds.playbackOptions(animationStartTime=True, query=True)
        animationEndTime = cmds.playbackOptions(animationEndTime=True, query=True)
        result = method(*args, **kw)
        cmds.playbackOptions(minTime=minTime, maxTime=maxTime, animationStartTime=animationStartTime, animationEndTime=animationEndTime)
        return result
    return namespace


def handleError(f):
    """ Decorator used for exiting Mayabatch/py with the corresponding exitcode. """
    @functools.wraps(f)
    def handleProblems(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, err:
            logger.critical(err, exc_info=True)
            quitMayapy(1)
    return handleProblems


@contextlib.contextmanager
def handleErrorContext():
    try:
        yield
    except Exception, err:
        logger.critical(err, exc_info=True)
        quitMayapy(1)


def viewportOff(func):
    """Decorator - turn off Maya display while func is running.
    if func will fail, the error will be raised after.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            # Turn $gMainPane Off, only possible in GUI mode
            cmds.paneLayout(getMayaGlobals('gMainPane'), edit=True, manage=False)
            disabled = True
        except:
            disabled = False

        # Decorator will try/except running the function.
        # But it will always turn on the viewport at the end.
        # In case the function failed, it will prevent leaving maya viewport off.
        try:
            return func(*args, **kwargs)
        except Exception:
            raise  # will raise original error
        finally:
            if disabled:
                cmds.paneLayout(getMayaGlobals('gMainPane'), edit=True, manage=True)
    return wrap


class viewportOffContext(object):
    def __enter__(self):
        try:
            cmds.paneLayout(getMayaGlobals('gMainPane'), edit=True, manage=False)
            self.disabled = True
        except:
            self.disabled = False

    def __exit__(self, *exc_info):
        if self.disabled:
            cmds.paneLayout(getMayaGlobals('gMainPane'), edit=True, manage=True)
