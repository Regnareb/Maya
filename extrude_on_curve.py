def create_curve():
    try:
        cmds.curveEPCtx("curveEP", degree=1)
    except RuntimeError:
        pass
    cmds.setToolTo("curveEP")
    cmds.scriptJob(runOnce = True, event = ("SelectionChanged", "executed_after_action()"))


def executed_after_action():
    selection = cmds.ls(sl=True)
    if not cmds.filterExpand(selection, selectionMask=9):
        cmds.scriptJob(runOnce = True, event = ("SelectionChanged", "executed_after_action()"))
        return
    createlocators(selection[0])
    

def createlocators(curve):
    cpPositions = cmds.getAttr(curve + '.controlPoints[*]')
    locators = []
    for index, position in enumerate(cpPositions):
        locators.append(cmds.spaceLocator()[0])
        cmds.scale(5, 5, 5)
        cmds.move(*position)
        # if not index:
        #     continue
        cmds.connectAttr('{}.translate'.format(locators[index]), '{}.controlPoints[{}]'.format(curve, index), force=True)

    plane = cmds.polyPlane(sx=1, sy=1, constructionHistory=False)
    cmds.move(*cpPositions[0])
    cmds.scale(5,5,5)
    constraint = cmds.aimConstraint(locators[1], plane, aimVector=(0, 1, 0), upVector=(0, 0, 1))
    cmds.delete(constraint)
    cmds.polyExtrudeFacet(plane[0], inputCurve=curve, divisions=len(cpPositions)-1)


# createlocators('curve1')




create_curve()
