import re
import os
import inspect
import logging
import functools
import maya.mel as mel
import maya.cmds as cmds
import lib.lib as tdLib
import lib.stats as tdStats
logger = logging.getLogger(__name__)

initstats = tdStats.Stats('Gator', 'regnareb', '1')


class PatterNodeSelector(object):
    def __init__(self):
        self.window = 'br_Gator'
        self.title = 'Gator'
        self.shelfPath = cmds.internalVar(userShelfDir=True) + 'br_GatorShelf'
        self.preferences = {'settingsFrame':True,
                            'selectSource': True,
                            'reverseSelection': False,
                            'longNames': True,
                            'regex': False,
                            # 'high':False
                            }
        self.filtersType = {'mesh': False,
                            'nurbsCurve': False,
                            'nurbsSurface': False,
                            'lambert': False,
                            'file': False,
                            'camera': False,
                            'light': False,
                            'particle': False
                            }
        self.preferences = dict(self.preferences, **self.filtersType)
        self.typeUI = {'settingsFrame':'frameLayout',
                       'selectSource': 'checkBox',
                       'reverseSelection': 'checkBox',
                       'longNames': 'checkBox',
                       'regex': 'checkBox',
                       # 'high': 'checkBox',
                       'mesh': 'iconTextCheckBox',
                       'nurbsCurve': 'iconTextCheckBox',
                       'nurbsSurface': 'iconTextCheckBox',
                       'lambert': 'iconTextCheckBox',
                       'file': 'iconTextCheckBox',
                       'camera': 'iconTextCheckBox',
                       'light': 'iconTextCheckBox',
                       'particle': 'iconTextCheckBox'
                        }
        self.loadPrefs()
        self.createUI()
        initstats.emit('open')


    @property
    def sourceNode(self):
        return self._sourceNode


    @sourceNode.setter
    def sourceNode(self, value):
        """Store the short name of the node"""
        self.sourceShort = tdLib.shortNameOf(value)
        self._sourceNode = value


    @property
    def pattern(self):
        """Each time the attribute pattern is called, it will query its value in the UI
        then be modified depending if the user is working in Full Regex mode or not
        """
        pattern = cmds.textField(self.interface['patternField'], query=True, text=True)
        if not self.preferences['regex']:
            pattern = pattern.replace('*', '.*')
        return pattern


    @property
    def filters(self):
        """Return the list of all the activated filters"""
        return [filterType for filterType in self.filtersType if self.preferences[filterType]]


    @property
    def allNodes(self):
        """Return the long names of all nodes in the scene or short names depending on preferences"""
        self.allNodesLong = cmds.ls(long=self.preferences['longNames'], type=self.filters)
        self.allNodesShort = [i.split('|')[-1] for i in self.allNodesLong]
        return self.allNodesLong if self.preferences['longNames'] else self.allNodesShort


    def getSourceNode(self, *args):
        """Get the first selection and store it"""
        self.sourceNode = tdLib.getFirstSelection(longName=True)
        if hasattr(self, 'interface'):
            cmds.textField(self.interface['sourceField'], edit=True, text=self.sourceShort)


    def getPattern(self, *args):
        """If the pattern field is empty, put the short name of the source node in it"""
        if not self.pattern:
            cmds.textField(self.interface['patternField'], edit=True, text=self.sourceShort)
        self.listNodes()


    def listNodes(self, forceRefresh=True, *args):
        """List all nodes following the pattern in the UI and save the shelf"""
        pattern = self.pattern
        cmds.textScrollList(self.interface['listSelector'], edit=True, removeAll=True)
        if not forceRefresh:
            indices = self.allNodesLong if self.preferences['longNames'] else self.allNodesShort
            # if self.preferences['high']:
            #     indices = [i for i in indices if "_Hi" in i]
        else:
            indices = self.allNodes

        indices = [i for i in indices if re.search(pattern, i)]

        cmds.textScrollList(self.interface['listSelector'], edit=True, append=indices)
        self.saveShelf()


    def selectNodes(self, *args):
        """Select nodes based on the UI, and change the order of selection based on user's preferences"""
        if self.preferences['selectSource']:
            sourceNode = self.sourceNode
        else:
            sourceNode = None
        if self.preferences['reverseSelection']:
            cmds.select(cmds.textScrollList(self.interface['listSelector'], query=True, selectItem=True), sourceNode or None)
        else:
            cmds.select(sourceNode or None, cmds.textScrollList(self.interface['listSelector'], query=True, selectItem=True))


    def loadShelf(self):
        """Load the default shelf if one does not exists in the user's maya preferences"""
        try:
            mel.eval('source ', self.shelfPath)
            mel.eval('td_patterNodeSelector()')
        except RuntimeError:
            logger.debug('Loading default shelf.')
            filePath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'defaultShelf.mel')
            mel.eval('source "%s"' % filePath)
            mel.eval('td_patternDefaultShelf()')


    def saveShelf(self, *args):
        """Save the shelf in a mel file in user's maya preferences"""
        cmds.saveShelf( self.interface['shelfLayout'], self.shelfPath)


    def loadPrefs(self):
        """Load all preferences and create default ones if they do not exists"""
        for label in self.preferences:
            if cmds.optionVar(exists='pns_' + label):
                self.preferences[label] = cmds.optionVar(query='pns_' + label)
            else:
                cmds.optionVar(intValue=('pns_' + label, self.preferences[label]))


    def savePrefs(self, label, refresh, *args):
        """Save preferences in optionVars"""
        method = getattr(cmds, self.typeUI[label])
        argument = 'value' if 'heckBox' in self.typeUI[label] else 'collapsable'
        variable = {'query':True, argument:True}
        self.preferences[label] = method(self.interface[label], **variable)
        cmds.optionVar(intValue=('pns_' + label, self.preferences[label]))
        self.updateUI(label, refresh)


    def updateUI(self, label, refresh):
        """Update the UI each time an item change"""
        if label in frozenset(['selectSource', 'reverseSelection']):
            cmds.checkBox(self.interface['reverseSelection'], edit=True, editable=self.preferences['selectSource'])
            self.selectNodes()
        else:
            self.listNodes(forceRefresh=refresh)


    def createUI(self):
        """Draw the window"""
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        self.window = cmds.window(self.window, title=self.title)

        # setup = {'panelLayout':[cmds.panelLayout, {configuration:"horizontal2", panelSize:[2,0,1]}]}
        # for k, (class_, kwargs) in setup.iteritems():
        #     self.interface[k] = class_(**kwargs)

        self.interface = {}
        filterSizeButton = 25
        self.interface['panelLayout'] = cmds.paneLayout(configuration='horizontal2', paneSize=[2, 0, 1])
        self.interface['formLayout1'] = cmds.formLayout(numberOfDivisions=100)
        self.interface['sourceButton'] = cmds.button(label='Source', width=50, command=self.getSourceNode)
        self.interface['sourceField'] = cmds.textField(height=24, editable=False)
        self.interface['patternButton'] = cmds.button(label='Pattern', width=50, command=self.getPattern)
        self.interface['patternField'] = cmds.textField(height=24, alwaysInvokeEnterCommandOnReturn=True, enterCommand=self.listNodes, changeCommand=self.listNodes)

        self.interface['filtersLayout'] = cmds.formLayout(numberOfDivisions=100)
        self.interface['mesh'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_polyPlane.png', value=self.preferences['mesh'], changeCommand=functools.partial(self.savePrefs, 'mesh', True))
        self.interface['nurbsCurve'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_nurbsCurve.png', value=self.preferences['nurbsCurve'], changeCommand=functools.partial(self.savePrefs, 'nurbsCurve', True))
        self.interface['nurbsSurface'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_nurbsSurface.png', value=self.preferences['nurbsSurface'], changeCommand=functools.partial(self.savePrefs, 'nurbsSurface', True))
        self.interface['lambert'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_lambert.png', value=self.preferences['lambert'], changeCommand=functools.partial(self.savePrefs, 'lambert', True))
        self.interface['file'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_file.png', value=self.preferences['file'], changeCommand=functools.partial(self.savePrefs, 'file', True))
        self.interface['camera'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_camera.png', value=self.preferences['camera'], changeCommand=functools.partial(self.savePrefs, 'camera', True))
        self.interface['light'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_ambientLight.png', value=self.preferences['light'], changeCommand=functools.partial(self.savePrefs, 'light', True))
        self.interface['particle'] = cmds.iconTextCheckBox(width=filterSizeButton, height=filterSizeButton, image='out_particle.png', value=self.preferences['particle'], changeCommand=functools.partial(self.savePrefs, 'particle', True))

        cmds.setParent('..')

        self.interface['settingsFrame'] = cmds.frameLayout(collapsable=True, collapse=self.preferences['settingsFrame'], label='Settings', expandCommand=functools.partial(self.savePrefs, 'settingsFrame', False), collapseCommand=functools.partial(self.savePrefs, 'settingsFrame', False))
        self.interface['columnLayout'] = cmds.formLayout(numberOfDivisions=100)
        self.interface['selectSource'] = cmds.checkBox(value=self.preferences['selectSource'], label='Select Source', changeCommand=functools.partial(self.savePrefs, 'selectSource', False))
        self.interface['reverseSelection'] = cmds.checkBox(value=self.preferences['reverseSelection'], editable=self.preferences['selectSource'], label='Reverse Selection', changeCommand=functools.partial(self.savePrefs, 'reverseSelection', False))
        self.interface['longNames'] = cmds.checkBox(value=self.preferences['longNames'], label='Long Names', changeCommand=functools.partial(self.savePrefs, 'longNames', False))
        self.interface['regex'] = cmds.checkBox(value=self.preferences['regex'], label='Use Regex', changeCommand=functools.partial(self.savePrefs, 'regex', False))
        # self.interface['high'] = cmds.checkBox(value=self.preferences['high'], label='Use High', changeCommand=functools.partial(self.savePrefs, 'high', False))
        cmds.setParent('..')
        cmds.setParent('..')
        self.interface['listSelector'] = cmds.textScrollList(allowMultiSelection=True, selectCommand=self.selectNodes)

        self.interface['formLayout2'] = cmds.formLayout(numberOfDivisions=100, parent=self.interface['panelLayout'])
        self.interface['shelfLayout'] =  cmds.shelfLayout(height=41)
        self.loadShelf()

        cmds.formLayout(
            self.interface['formLayout1'], edit=True,
            attachForm=(
                [self.interface['sourceButton'], 'top', 5],
                [self.interface['sourceButton'], 'left', 5],
                [self.interface['sourceField'], 'top', 5],
                [self.interface['sourceField'], 'right', 5],
                [self.interface['patternButton'], 'left', 5],
                [self.interface['patternField'], 'right', 5],
                [self.interface['settingsFrame'], 'left', 0],
                [self.interface['settingsFrame'], 'right', 0],
                [self.interface['listSelector'], 'left', 0],
                [self.interface['listSelector'], 'right', 0],
                [self.interface['listSelector'], 'bottom', 0],
            ),
            attachControl=(
                [self.interface['patternButton'], 'top', 5, self.interface['sourceButton']],
                [self.interface['patternField'], 'top', 5, self.interface['sourceButton']],
                [self.interface['listSelector'], 'top', 5, self.interface['settingsFrame']],
                [self.interface['sourceField'], 'left', 5, self.interface['sourceButton']],
                [self.interface['patternField'], 'left', 5, self.interface['patternButton']],
                [self.interface['filtersLayout'], 'top', 5, self.interface['patternButton']],
                [self.interface['settingsFrame'], 'top', 5, self.interface['filtersLayout']],
            )
        )

        cmds.formLayout(
            self.interface['filtersLayout'], edit=True,
            attachControl=(
                [self.interface['light'], 'left', 0, self.interface['camera']],
                [self.interface['mesh'], 'left', 0, self.interface['light']],
                [self.interface['nurbsCurve'], 'left', 0, self.interface['mesh']],
                [self.interface['nurbsSurface'], 'left', 0, self.interface['nurbsCurve']],
                [self.interface['lambert'], 'left', 0, self.interface['nurbsSurface']],
                [self.interface['file'], 'left', 0, self.interface['lambert']],
                [self.interface['particle'], 'left', 0, self.interface['file']],
            )
        )

        cmds.formLayout(
            self.interface['columnLayout'], edit=True,
            attachForm=(
                [self.interface['selectSource'], 'top', 5],
                [self.interface['selectSource'], 'left', 5],
                [self.interface['reverseSelection'], 'top', 5],
                [self.interface['reverseSelection'], 'left', 125],
                [self.interface['longNames'], 'left', 5],
                [self.interface['longNames'], 'bottom', 5],
                [self.interface['regex'], 'left', 125],
                # [self.interface['high'], 'left', 5],
                # [self.interface['high'], 'bottom', 5],
            ),
            attachControl=(
                [self.interface['longNames'], 'top', 5, self.interface['selectSource']],
                [self.interface['regex'], 'top', 5, self.interface['reverseSelection']],
                # [self.interface['high'], 'top', 5, self.interface['longNames']],
            )
        )
        cmds.formLayout(
            self.interface['formLayout2'], edit=True,
            attachForm=(
                [self.interface['shelfLayout'], 'top', 0],
                [self.interface['shelfLayout'], 'left', 0],
                [self.interface['shelfLayout'], 'right', 0],
                [self.interface['shelfLayout'], 'bottom', 0],
            )
        )
        cmds.showWindow()
        self.createAnnotations()
        self.initUI()


    def initUI(self):
        self.getSourceNode()
        cmds.textField(self.interface['sourceField'], edit=True, text=self.sourceShort)
        cmds.textField(self.interface['patternField'], edit=True, text=self.sourceShort)
        cmds.setFocus(self.interface['patternField'])
        self.listNodes()


    def createAnnotations(self):
        self.annotation = {
            'sourceButton': 'Click to update the Source node base on the current selection.',
            'patternButton': 'Click to update the node list,\nOr to copy the Source node name if no pattern is specified.',
            'patternField': 'Filter the nodes with this specific pattern.\nPut a \'*\' if you want any characters to be accepted.',
            'selectSource': 'If checked, it will select the source node + the one selected in the list.\nIf not checked, it will only select the ones selected in the list.',
            'reverseSelection': 'If checked, the Source node will be selected last.',
            'longNames': 'If checked, it will display the full path of the nodes in the list.',
            'regex': 'If you want to use real Regex syntax. By default the \'*\' joker means \'.*\'.\n\nIn Regex mode:\n.* will search for anything\n$ means it is the end of the word',
            'shelfLayout': 'You can put any tool you want in this shelf.\nIt is saved if you reevaluate the list of the nodes filtered.',
            'mesh': 'Polygons',
            'nurbsCurve': 'Curves',
            'nurbsSurface': 'NURBS',
            'lambert': 'Materials',
            'file': 'Textures',
            'camera': 'Cameras',
            'light': 'Lights',
            'particle': 'Particles',
        }
        for label in self.annotation:
            typeUI = tdLib.shortNameOf(self.interface[label]).rstrip('1234567890')
            method = getattr(cmds, typeUI)
            method(self.interface[label], edit=True, annotation=self.annotation[label])
