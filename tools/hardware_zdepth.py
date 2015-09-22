import maya.cmds as cmds
import lib.lib as tdLib

camera = tdLib.getActiveCamera() or 'persp'

allGeo = cmds.ls(geometry=True)
allGeo = cmds.filterExpand(allGeo, selectionMask=12)

# create shader
material = cmds.shadingNode('surfaceShader', asShader=True)
sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=(material + "SG"))
cmds.connectAttr(material + '.outColor', sg + '.surfaceShader', force=True)

# assign shader
cmds.sets(allGeo, edit=True, forceElement=sg)

# Create projection rig
projection = cmds.shadingNode('projection', asTexture=True)
place3d = cmds.shadingNode('place3dTexture', asUtility=True)
cmds.connectAttr(place3d + '.worldInverseMatrix', projection + '.placementMatrix')
cmds.connectAttr(projection + '.outColor', material + '.outColor')
cmds.parent(place3d, camera)
cmds.move(0, 0, 0, place3d, objectSpace=True)
cmds.setAttr(projection + '.blend', 1)
cmds.setAttr(projection + '.projType', 4)
cmds.setAttr(projection + '.image', 1, 1, 1, type='double3')
cmds.setAttr(projection + '.defaultColor', 0, 0, 0, type='double3')

# Set far distance
farDistance = 100
cmds.scale(farDistance, farDistance, farDistance, place3d)
