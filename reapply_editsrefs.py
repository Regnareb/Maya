import logging
import maya.mel as mel
import lib.lib as tdLib
logger = logging.getLogger(__name__)

def applyEdits(editCommands, pattern=''):
    for commands in editCommands:
        if pattern:
            commands = [cmd for cmd in commands if pattern.lower() not in cmd.lower()]

        for cmd in commands:
            try:
                mel.eval(cmd)
            except RuntimeError:
                pass

def getEdits(refNode):
    refEdits = []
    editCommands = ['parent', 'deleteAttr', 'addAttr', 'disconnectAttr', 'setAttr', 'connectAttr']
    for i in editCommands:
        refEdits.append(cmds.referenceQuery(refNode, editStrings=True, editCommand=i))
    return refEdits

references = tdLib.getReferences(True)

# Query edits strings
for ref in references.values():
    ref['editsRef'] = getEdits(ref['refNode'])
    if not ref['isLoaded']:
        ref['editsRef'] = [[command.replace('|..:', '|:') for command in grpCommands] for grpCommands in ref['editsRef']]

# Cleanup and load references
for ref in references:
    if references[ref]['isLoaded']:
        cmds.file(unloadReference=references[ref]['refNode'])
        cmds.file(cleanReference=references[ref]['refNode'])
        cmds.file(loadReference=references[ref]['refNode'])

        # Reapply edits strings
# for ref in references:
    # if references[ref]['isLoaded']:
        cmds.namespace(set=ref)
        cmds.namespace(relativeNames=True)
        applyEdits(references[ref]['editsRef'])
        cmds.namespace(relativeNames=False)
        cmds.namespace(set=':')




