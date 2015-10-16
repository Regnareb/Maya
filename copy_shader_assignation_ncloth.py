import lib.lib as tdLib


OBJS = []
OBJSCOPY = []

selection = cmds.ls(sl=True, dagObjects=True)
selection = cmds.ls(selection, shapes=True)


for sel in selection:
    try:
        ncloth = tdLib.getFirstItem(cmds.listConnections(sel + '.inMesh', source=True, shapes=True))
        shape = tdLib.getFirstItem(cmds.listConnections(ncloth + '.inputMesh', source=True, shapes=True))
        OBJS.append(shape)
        OBJSCOPY.append(sel)
    except TypeError:
        pass


shadingGroups = list(tdLib.flatten([tdLib.getSGsFromShape(i) for i in OBJS]))
shaders = [tdLib.getMaterialFromSG(i) for i in shadingGroups]
assignation = {}
for i in shaders:
    assignation[i] = tdLib.getShaderAssignation(i)


objs = {}
for i, u in zip(OBJS, OBJSCOPY):
    objs[i] = u

assignationNew = {}
for shader, assign in assignation.iteritems():
    assignationNew[shader] = []
    for ass in assign:
        splitted = ass.split('.')[0]
        try:
            assignationNew[shader].append(ass.replace(splitted, objs[splitted]))
        except KeyError, e:
            pass

for shader, meshes in assignationNew.iteritems():
    cmds.select(meshes)
    cmds.hyperShade(assign=shader)

