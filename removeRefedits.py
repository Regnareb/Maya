import lib.libmaya as libmaya

def getEdits(refNode):
    editCommands = ['disconnectAttr', 'setAttr', 'connectAttr']
    refEdits = {i: [] for i in editCommands}
    for key, val in refEdits.iteritems():
        val[:] = list(set(cmds.referenceQuery(refNode, editStrings=True, editCommand=key, showDagPath=False)))
    return refEdits

references = libmaya.getReferences(True)
ref = references['Yourref']
ref['editsRef'] = getEdits(ref['refNode'])

['wl[', 'weightList[', 'lodVisibility', 'overrideEnabled', 'output']

pattern = 'wl['

for editType, edits in ref['editsRef'].iteritems():
    finalList = []
    for i in edits:
        if pattern in i:
            toDel = i.split(' ')[1]
            finalList.append('Yourref:' + toDel.split('.')[0])
            cmds.referenceEdit('Yourref:' + toDel, failedEdits=True, successfulEdits=True, editCommand=editType, removeEdits=True) # For the attribute

    # For the node
    finalList = list(set(finalList))
    for i in finalList:
        cmds.referenceEdit(i, failedEdits=True, successfulEdits=True, editCommand=editType, removeEdits=True)


