import os
import shutil
import maya.cmds as cmds

__version__ = '1.0.0'

def nodeLockSet(lockFlag, nodeList):
    result = []
    for nodeName in nodeList:
        if cmds.objExists(nodeName) == False :
            continue
        if cmds.referenceQuery(nodeName, isNodeReferenced=True):
            continue
        cmds.lockNode(nodeName, lock=lockFlag)
        result.append(nodeName)
    return result


def nodeLockQuery(lockFlag, nodeList):
    result = []
    for nodeName in nodeList:
        if cmds.objExists(nodeName) == False:
            continue
        tmp = cmds.lockNode(nodeName, q=True)
        if tmp[0] == lockFlag:
            result.append(nodeName)
    return result


def arrayRemoveElement(patternSearchList, objectList, removeDuplicate):
    result = []
    for objectName in objectList:
        flag = False
        for patternSearchName in patternSearchList:
            if re.match(patternSearchName, objectName):
                flag = True
                break
        if flag == False:
            result.append(objectName)
    if removeDuplicate:
        result = list(set(result))
    return result


def loadMentalRayPlugin():
    listAll = cmds.ls()
    nodeLockList        = nodeLockQuery(True, listAll)
    nodeList            = arrayRemoveElement( ["^(.*)RN$"], nodeLockList, True)

    plugsList = cmds.pluginInfo(q=True, listPlugins=True)

    if 'Mayatomr' not in plugsList:
        nodeLockSet( False, nodeList )
        cmds.loadPlugin('Mayatomr', quiet=True)
        nodeLockSet( True, nodeList )
        plugsList = cmds.pluginInfo(q=True, listPlugins=True)

        if 'Mayatomr' not in plugsList:
            cmds.error('Can\'t load Mental Ray plugin...')
            return False


def getShapes( xform ):
    if cmds.nodeType( xform ) == 'transform':
        shapes = cmds.listRelatives( xform, fullPath=True, shapes=True)
    return shapes


def getCameras():
    allCameras      = cmds.listCameras(perspective=True)
    selection       = cmds.ls(sl=True)
    renderCamera    = [i for i in allCameras if i in selection]
    for camera in allCameras:
        cmds.setAttr( getShapes(camera)[0] + '.renderable', 0)
    for camera in renderCamera:
        cmds.setAttr( getShapes(camera)[0] + '.renderable', 1)
    return renderCamera




userLogin  = os.environ['USER']
loadMentalRayPlugin()
cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type='string')
cmds.setAttr('defaultRenderGlobals.imageFormat', 32 )

camerasList = getCameras()
focalList   = [ 20, 25, 30, 35 ]
startTime   = cmds.playbackOptions( query=True, minTime=True)
endTime     = cmds.playbackOptions( query=True, maxTime=True)

for camera in camerasList:
    renderKeys = sorted( list( set( cmds.keyframe( camera, time=(startTime, endTime), query=True ))))
    for key in renderKeys:
        for focal in focalList:
            cmds.currentTime( key, edit=True )
            cmds.setAttr( getShapes(camera)[0] + '.focalLength', focal )
            tempPath = cmds.Mayatomr( preview=True, cam=camera )
            extension = os.path.splitext( tempPath )[1]
            finalPath = '/Desktop/render/%s_key%s_focal%s%s' % ( camera.replace(':', '_'), int(key), focal, extension )
            shutil.move( tempPath, finalPath )
            
            
