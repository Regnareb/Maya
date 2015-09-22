# Dirty dirty dirty!

import colorsys
current = cmds.polyCube(name="rainbow0")
cmds.setKeyframe(attribute='translateX', t=1, v=0)
cmds.setKeyframe(attribute='translateX', t=11, v=-1.317)
cmds.setKeyframe(attribute='translateX', t=22, v=-2.533)
curve = current[0] + '_translateX'
cmds.setAttr(curve + '.useCurveColor', 1)
offset = 0.85 # -1.167 for stripped flag
cmds.setAttr(curve + '.curveColor', *colorsys.hsv_to_rgb(offset, 0.8, 1), type='double3')
cmds.setAttr(curve + ".kix[0:2]", 0.052, 0.017, 0.022, s=3)
cmds.setAttr(curve + ".kiy[0:2]", 1, -1, -1, s=3)
cmds.setAttr(curve + ".kox[0:2]", 0.052, 0.0172, 0.022, s=3)
cmds.setAttr(curve + ".koy[0:2]", 1, -1, -1, s=3)
cmds.group()

nbDupli = 1000
for i in xrange(nbDupli):
    current = cmds.duplicate(current, upstreamNodes=True)
    cmds.keyframe(current[1], edit=True, relative=True, valueChange=1.5/float(nbDupli)*10)
    cmds.setAttr(current[1] + '.curveColor', *colorsys.hsv_to_rgb(offset+i/-float(nbDupli), 0.8, 1), type='double3')

cmds.select(hierarchy=True)

