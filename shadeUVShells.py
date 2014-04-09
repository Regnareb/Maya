"""
Get all the shells of each selected object.
Then assign a surface shader to each shell with a different random color
"""

import random
import logging
import colorsys
import maya.cmds as cmds
import maya.OpenMaya as om
logger = logging.getLogger(__name__)

__version__ = '1.0.0'
__author__ = 'Regnareb'

def shadeUVShells():


    uvSet = 'map1'
    data = []
    shellDict = {}
    goldenRatio = 0.618033988749895 # use golden ratio


    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( selList )
    selListIter = om.MItSelectionList( selList, om.MFn.kMesh )
    uvShellArray = om.MIntArray()

    while not selListIter.isDone():
        pathToShape = om.MDagPath()
        selListIter.getDagPath(pathToShape)
        meshNode = pathToShape.fullPathName()

        uvSets = cmds.polyUVSet( meshNode, query=True, allUVSets =True )

        if (uvSet in uvSets):
            shapeFn = om.MFnMesh(pathToShape)
            shells = om.MScriptUtil()
            shells.createFromInt(0)
            shellsPtr = shells.asUintPtr()
            shapeFn.getUvShellsIds(uvShellArray, shellsPtr, uvSet)

        # Convert uvShellArray
        for index, value in enumerate(uvShellArray):
            shellDict.setdefault(value,[]).append(index)

        # Assign shaders
        for index, value in shellDict.iteritems():
            shaderNode = cmds.shadingNode( 'surfaceShader', asShader=True )
            faceShell = cmds.polyListComponentConversion( [('%s.map[%s]' % ( meshNode, u )) for u in value ], toFace=True )
            cmds.select( faceShell )
            cmds.hyperShade( assign=shaderNode )

            hue = random.random()
            hue += goldenRatio
            hue %= 1

            rgbColor = colorsys.hsv_to_rgb(hue, random.uniform(0.8, 1), random.uniform(0.8, 1))
            cmds.setAttr( shaderNode + ".outColor", *rgbColor, type="double3" )

        shellDict.clear()
        uvShellArray.clear()
        selListIter.next()

    cmds.select(clear=True)



