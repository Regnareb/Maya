import os
import time

class SceneInfo(object):
    INTERACTIVE = 0
    BATCH = 1
    MAYAPY = 2

    # def _getCmdsFile(self, **kwargs):
    #     return cmds.file(**kwargs)
    #     return self._getCmdsFile(dict(query=True, sceneName=True, shortName=True))

    @property
    def path(self):
        return cmds.file(query=True, sceneName=True)

    @property
    def unresolvedPath(self):
        return cmds.file(query=True, sceneName=True, unresolved=True)

    @property
    def name(self):
        return cmds.file(query=True, sceneName=True, shortName=True)
# expandName ?

    @property
    def size(self):
        return os.path.getsize(self.path)

    @property
    def dateModified(self):
        return time.ctime(os.path.getmtime(self.path))

    @property
    def dateCreation(self):
        return time.ctime(os.path.getctime(self.path))

    @property
    def modified(self):
        return cmds.file(query=True, modified=True)

    @property
    def errorStatus(self):
        return cmds.file(query=True, errorStatus=True)


    @property
    # persistent
    def batch(self):
        if hasattr(self, '_batch'):
            return self._batch
        try:
            import maya.standalone
            maya.standalone.initialize()
        except RuntimeError:
            self._batch = cmds.about(batch=True)
        else:
            self._batch = 2
        return self._batch




    @property
    def meshes(self):
        return cmds.ls(long=True, type="mesh")

    @property
    def transforms(self):
        return cmds.ls(long=True, type="transforms")

    @property
    def shapes(self):
        return cmds.ls(long=True, type="shapes")

    @property
    def locked(self):
        cmds.ls(long=True, lockedNode=True)



















def nodeIsVisible(node=None):
    if not node:
        node = cmds.ls(sl=True)

    if not cmds.objExists(node) or cmds.attributeQuery('visibility', node=node, exists=True):
        raise NameError('That node does not exists.')





















    @property
    def visible(self):
        return cmds.ls(long=True, visible=True)

    @property
    def hidden(self):
        return cmds.ls(long=True, invisible=True)

    @property
    def materials(self):

    @property
    def shadingGroups(self):

    @property
    def curves(self):

    @property
    def animCurves(self):

    @property
    def nurbs(self):

    @property
    def deformers(self):

    @property
    def clusters(self):

    @property
    def lattices(self):

    @property
    def blendshapes(self):

    @property
    def wires(self):

    @property
    def joints(self):

    @property
    def cameras(self):

    @property
    def textures(self):

    @property
    def lights(self):

    @property
    def sets(self):

    @property
    def shaderAssignation(self):

    @property
    def allNodes(self):

    @property
    def referencesDict(self):
        """Returns a dictionary with the path to the ref, its refNode, the nodes contained in the ref, and if the ref is loaded or not"""
        references = cmds.file(query=True, reference=True)
        referencesDict = dict()
        for ref in references:
            refNode = cmds.file(ref, query=True, referenceNode=True)
            isLoaded = cmds.referenceQuery(refNode, isLoaded=True)
            nodesInRef = cmds.referenceQuery(refNode, nodes=True)
            referencesDict[ref] = [refNode, nodesInRef, isLoaded]
        return referencesDict

    @property
    def pluginsLoaded(self):
        pass

    @property
    def pluginsAvailable(self):





""" From Pymel """

from getpass import getuser as _getuser

    def getConstructionHistory(self):
        return cmds.constructionHistory( q=True, tgl=True )

    def sceneName(self):
        return system.Path(cmds.file( q=1, sn=1))

    def getUpAxis(self):
        """This flag gets the axis set as the world up direction. The valid axis are either 'y' or 'z'."""
        return cmds.upAxis( q=True, axis=True )

    def getTime( self ):
        return cmds.currentTime( q=1 )

    def getMinTime( self ):
        return cmds.playbackOptions( q=1, minTime=1 )

    def getMaxTime( self ):
        return cmds.playbackOptions( q=1, maxTime=1 )

    def getAnimStartTime( self ):
        return cmds.playbackOptions( q=1, animationStartTime=1 )

    def getAnimEndTime( self ):
        return cmds.playbackOptions( q=1, animationEndTime=1 )

    def user(self):
        return _getuser()
    def host(self):
        return _gethostname()
