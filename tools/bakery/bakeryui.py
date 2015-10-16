import os
import logging
import functools
import webbrowser
from PySide import QtCore, QtGui
import lib.qtwrapper as qtwrapper
import bakery as b
import lib.tdLib as tdLib

logger = logging.getLogger(__name__)


class FloatSlider(QtGui.QSlider):
    """Create a slider able to return floats as a value."""
    def __init__(self, parent, decimals=3, *args, **kargs):
        super(FloatSlider, self).__init__(parent, *args, **kargs)
        self._multi = 10 ** decimals
        self.setMinimum(self.minimum())
        self.setMaximum(self.maximum())

    def value(self):
        return float(super(FloatSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(FloatSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(FloatSlider, self).setMaximum(value * self._multi)

    def setValue(self, value):
        super(FloatSlider, self).setValue(int(value * self._multi))



class RowLayout(QtGui.QHBoxLayout):
    """An object where you are able to add different UI elements easily and automatically."""
    def __init__(self, parent=None):
        super(RowLayout, self).__init__()
        self.parent = parent
        self.labels = []
        self.fields = []
        self.sliders = []
        self.spacers = []
        self.buttons = []
        self.comboboxes = []
        self.toolbuttons = []
        self.checkboxes = []
        self.separators = []

    def addLabel(self, text=''):
        self.label = QtGui.QLabel(self.parent)
        self.label.setText(text)
        self.label.setMinimumSize(QtCore.QSize(125, 19))
        self.label.setMaximumSize(QtCore.QSize(125, 16777215))
        self.labels.append(self.label)
        self.addWidget(self.label)

    def addSpacer(self):
        self.spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.spacers.append(self.spacer)
        self.addItem(self.spacer)
        return self.spacer

    def addField(self, validator='', minimum=None, maximum=None, decimals=3):
        if validator == 'float':
            self.field = QtGui.QDoubleSpinBox(self.parent)
            self.field.setDecimals(decimals)
            self.field.setSingleStep(0.5)
            self.field.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
        else:
            self.field = QtGui.QSpinBox(self.parent)
        self.field.setAccelerated(True)
        self.field.setMinimumSize(QtCore.QSize(70, 0))
        self.field.setMaximumSize(QtCore.QSize(70, 16777215))
        self.field.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        if minimum:
            self.field.setMinimum(minimum)
        if maximum:
            self.field.setMaximum(maximum)
        self.fields.append(self.field)
        self.addWidget(self.field)
        return self.field

    def addSlider(self, mode='', minimum=None, maximum=None):
        if mode == 'float':
            self.slider = FloatSlider(self.parent)
        else:
            self.slider = QtGui.QSlider(self.parent)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        if minimum is not None:
            self.slider.setMinimum(minimum)
        if maximum is not None:
            self.slider.setMaximum(maximum)
        self.sliders.append(self.slider)
        self.addWidget(self.slider)
        return self.slider

    def addCombobox(self, items=[]):
        self.combobox = QtGui.QComboBox(self.parent)
        for item in items:
            self.combobox.addItem(item)
        self.comboboxes.append(self.combobox)
        self.addWidget(self.combobox)
        return self.combobox

    def addToolbutton(self):
        self.toolbutton = QtGui.QToolButton(self.parent)
        self.toolbuttons.append(self.toolbutton)
        self.addWidget(self.toolbutton)
        return self.toolbutton

    def addCheckbox(self, state=False):
        self.checkbox = QtGui.QCheckBox(self.parent)
        self.checkbox.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
        self.checkboxes.append(self.checkbox)
        self.addWidget(self.checkbox)
        return self.checkbox

    def addButton(self, label='', size=None):
        self.button = QtGui.QPushButton(self.parent)
        self.button.setText(label)
        if size:
            self.button.setMaximumSize(QtCore.QSize(size, size))
        self.buttons.append(self.button)
        self.addWidget(self.button)
        return self.button

    def addSeparator(self):
        self.separator = QtGui.QFrame(self.parent)
        self.separator.setFrameShape(QtGui.QFrame.HLine)
        self.separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.separators.append(self.separator)
        self.addWidget(self.separator)
        return self.separator

    def createValidator(self, validator, minimum=None, maximum=None, decimals=3):
        if validator == 'int':
            self.field.setValidator(QtGui.QIntValidator(minimum, maximum, self))
        elif validator == 'float':
            self.field.setValidator(QtGui.QDoubleValidator(minimum, maximum, decimals, self))
        else:
            return False
        return True

    def connectFieldSlider(self):
        self.field.valueChanged.connect(self.toSlider)
        self.slider.valueChanged.connect(self.toField)

    def toField(self, *args):
        self.field.setValue(self.slider.value())

    def toSlider(self, *args):
        self.slider.setValue(args[0])

    def setText(self, texts):
        for label, text in zip(self.labels, texts):
            label.setText(text)

    def setValue(self, values):
        for field, value in zip(self.fields, values):
            field.setValue(value)
        for checkbox, state in zip(self.checkboxes, values):
            checkbox.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)

    def setItem(self, items):
        for combobox, item in zip(self.comboboxes, items):
            combobox.setCurrentIndex(item)

    def getValue(self):
        values = []
        for field in self.fields:
            values.append(field.valueFromText(field.text()))
        for combobox in self.comboboxes:
            values.append(combobox.currentIndex())
        for checkbox in self.checkboxes:
            state = checkbox.checkState()
            values.append(bool(state))
        return values

    def hide(self):
        for widget in self.labels + self.fields + self.sliders + self.comboboxes + self.toolbuttons + self.checkboxes + self.separators + self.buttons:
            widget.hide()

    def show(self):
        for widget in self.labels + self.fields + self.sliders + self.comboboxes + self.toolbuttons + self.checkboxes + self.separators + self.buttons:
            widget.show()

    def setToolTip(self, tip):
        for widget in self.labels + self.fields + self.sliders + self.comboboxes + self.toolbuttons + self.checkboxes + self.separators + self.buttons:
            widget.setToolTip(tip)

    def setStatusTip(self, tip):
        for widget in self.labels + self.fields + self.sliders + self.comboboxes + self.toolbuttons + self.checkboxes + self.separators + self.buttons:
            widget.setToolTip(tip)


class BakeryUI(object):
    def __init__(self, MainWindow, Bakery):
        b.initstats.emit('open')
        self.shaders = {}
        self.menubar = {}
        self.Bakery = Bakery
        self.MainWindow = MainWindow
        self.mode = 'OCC'
        self._currentShaderButton = None
        self.settings = QtCore.QSettings("tdTools", "TheBakery")
        self.convertMode = {'OCC': 'occlusion', 'THICK': 'thickness', 'DIRT': 'dirt', 'RGB': 'rgb'}
        self.interface = {i:{} for i in ['maintabs', 'attributes', 'finalbuttons', 'shaders'] + self.convertMode.keys()}

    def setupUi(self):
        """Create all the UI elements"""
        self.window = QtGui.QMainWindow(self.MainWindow)
        self.window.closeEvent = self.closeEvent
        self.window.setStyleSheet("QToolTip {font-size:9pt;padding:2px}");
        self.centralwidget = QtGui.QWidget(self.window)
        self.centralwidget.setMinimumWidth(350)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)

        self.interface['maintabs']['layout'] = QtGui.QHBoxLayout()
        self.interface['maintabs']['buttonGroup'] = QtGui.QButtonGroup()
        self.interface['maintabs']['occlusion'] = QtGui.QPushButton(self.centralwidget)
        self.interface['maintabs']['occlusion'].setMinimumSize(QtCore.QSize(0, 30))
        self.interface['maintabs']['occlusion'].setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.interface['maintabs']['thickness'] = QtGui.QPushButton(self.centralwidget)
        self.interface['maintabs']['thickness'].setMinimumSize(QtCore.QSize(0, 30))
        self.interface['maintabs']['thickness'].setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.interface['maintabs']['dirt'] = QtGui.QPushButton(self.centralwidget)
        self.interface['maintabs']['dirt'].setMinimumSize(QtCore.QSize(0, 30))
        self.interface['maintabs']['dirt'].setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.interface['maintabs']['rgb'] = QtGui.QPushButton(self.centralwidget)
        self.interface['maintabs']['rgb'].setMinimumSize(QtCore.QSize(0, 30))
        self.interface['maintabs']['rgb'].setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.interface['maintabs']['occlusion'].clicked.connect(lambda: self.addShaders('OCC'))
        self.interface['maintabs']['thickness'].clicked.connect(lambda: self.addShaders('THICK'))
        self.interface['maintabs']['dirt'].clicked.connect(lambda: self.addShaders('DIRT'))
        self.interface['maintabs']['rgb'].clicked.connect(lambda: self.addShaders('RGB'))
        self.interface['maintabs']['buttonGroup'].addButton(self.interface['maintabs']['occlusion'], 1)
        self.interface['maintabs']['buttonGroup'].addButton(self.interface['maintabs']['thickness'], 2)
        self.interface['maintabs']['buttonGroup'].addButton(self.interface['maintabs']['dirt'], 3)
        self.interface['maintabs']['buttonGroup'].addButton(self.interface['maintabs']['rgb'], 4)
        self.interface['maintabs']['layout'].addWidget(self.interface['maintabs']['occlusion'])
        self.interface['maintabs']['layout'].addWidget(self.interface['maintabs']['thickness'])
        self.interface['maintabs']['layout'].addWidget(self.interface['maintabs']['dirt'])
        self.interface['maintabs']['layout'].addWidget(self.interface['maintabs']['rgb'])
        self.verticalLayout.addLayout(self.interface['maintabs']['layout'])

        self.interface['attributes']['layout'] = QtGui.QVBoxLayout()
        self.verticalLayout.addLayout(self.interface['attributes']['layout'])

        self.interface['finalbuttons']['layout'] = QtGui.QHBoxLayout()
        self.interface['finalbuttons']['preview'] = QtGui.QPushButton(self.centralwidget)
        self.interface['finalbuttons']['preview'].setMinimumSize(QtCore.QSize(150, 40))
        self.interface['finalbuttons']['preview'].clicked.connect(self.preview)
        self.interface['finalbuttons']['layout'].addWidget(self.interface['finalbuttons']['preview'])
        self.interface['finalbuttons']['interactivebake'] = QtGui.QPushButton(self.centralwidget)
        self.interface['finalbuttons']['interactivebake'].setMinimumSize(QtCore.QSize(-20, 40))
        self.interface['finalbuttons']['interactivebake'].clicked.connect(self.bakeInteractive)
        self.interface['finalbuttons']['layout'].addWidget(self.interface['finalbuttons']['interactivebake'])
        self.interface['finalbuttons']['bake'] = QtGui.QPushButton(self.centralwidget)
        self.interface['finalbuttons']['bake'].setMinimumSize(QtCore.QSize(150, 40))
        self.interface['finalbuttons']['bake'].clicked.connect(self.bake)
        self.interface['finalbuttons']['layout'].addWidget(self.interface['finalbuttons']['bake'])
        self.interface['finalbuttons']['spacer'] = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addLayout(self.interface['finalbuttons']['layout'])
        self.verticalLayout.addItem(self.interface['finalbuttons']['spacer'])
        self.interface['maintabs']['layout'].setSpacing(0)
        self.interface['finalbuttons']['layout'].setSpacing(0)

        self.createDockShaders()
        self.createMenuBar()
        self.createPresetsBar()
        self.createUdimsBar()
        self.createAttributesLayout()
        self.updateFinalButtons()
        self.retranslateUi()
        self.createTooltips()
        self.window.setCentralWidget(self.centralwidget)
        self.addShadersToUI(self.Bakery.shaders)

    def createDockShaders(self):
        """Create the basic elements of the right part of the UI where the shader are displayed"""
        def savedockposition(area):
            area = tdLib.camelCaseSeparator(str(area).split('.')[-1]).split(' ')[0]
            self.settings.setValue('DockPosition', area)
        self.interface['shaders']['groupbox'] = QtGui.QWidget(self.centralwidget)
        self.interface['shaders']['layout'] = QtGui.QVBoxLayout(self.centralwidget)
        self.interface['shaders']['groupbox'].setLayout(self.interface['shaders']['layout'])
        self.interface['shaders']['buttonGroup'] = QtGui.QButtonGroup()
        self.interface['shaders']['buttonGroup'].setExclusive(False)
        self.verticalLayout.addWidget(self.interface['shaders']['groupbox'])
        self.interface['shaders']['spacer'] = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.interface['shaders']['layout'].addItem(self.interface['shaders']['spacer'])

        self.dock = QtGui.QDockWidget('Shaders', self.centralwidget)
        self.dock.dockLocationChanged.connect(savedockposition)
        self.dock.setMinimumWidth(300)
        self.dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
        area = self.settings.value('DockPosition') or 'Right'
        self.window.addDockWidget(getattr(QtCore.Qt.DockWidgetArea, area + 'DockWidgetArea'), self.dock)
        self.dock.setWidget(self.interface['shaders']['groupbox'])

    def createMenuBar(self):
        """Create all the menus at the top of the UI."""
        def addaction(method, *args):
            if default:
                titl = ''.join([title, ' (Default)'])
            else:
                titl = title
            action = QtGui.QAction(QtGui.QIcon(''), titl, self.window)
            action.setCheckable(True)
            if not titl:
                action.setSeparator(True)
            elif method:
                action.triggered.connect(functools.partial(method, *args))
            action.setShortcut(shortcut)
            menu.addAction(action)
            if group:
                group.addAction(action)
            return action

        supaDict = {'order': ['Preset', 'Preview', 'Export'],
                    'Preset': {'prefs': [('Draft', 'draft'), ('Low', 'low'), ('Medium', 'medium'), ('High', 'high'), ('Very High', 'veryHigh')],
                               'method': self.Bakery.setPreference,
                               'default': 'high',
                               'shortcuts': {'Draft': 'Ctrl+1', 'Low': 'Ctrl+2', 'Medium': 'Ctrl+3', 'High': 'Ctrl+4', 'Very High': 'Ctrl+5'},
                               },
                    'Preview': {'prefs': [('Render', '-0'), ('', ''), ('10%', '10'), ('25%', '4'), ('50%', '2'), ('75%', '1.33'), ('100%', '1')],
                                'method': self.Bakery.setPreference,
                                'default': '4',
                                'shortcuts': {'Render': 'Alt+0', '10%': 'Alt+1', '25%': 'Alt+2', '50%': 'Alt+3', '75%': 'Alt+4', '100%': 'Alt+5'},
                                },
                    'Export': {'prefs': [('Auto', 'auto'), ('Force All', 'all'), ('Selection', 'selection'), ('Open Original Scene', 'original'), ('', '')],
                               'method': self.Bakery.setPreference,
                               'default': 'auto',
                               'shortcuts': {},
                               }
                    }
        for item in supaDict['order']:
            self.menubar[item] = {}
            menu = self.window.menuBar().addMenu(item.title())
            group = QtGui.QActionGroup(self.window)
            for pres in supaDict[item]['prefs']:
                title = pres[0]
                value = pres[1]
                default = value == supaDict[item]['default']
                shortcut = supaDict[item]['shortcuts'].get(title)
                action = addaction(supaDict[item]['method'], item, value)
                pref = self.Bakery.getPreference(item)
                if pref == None and default or self.Bakery.getPreference(item) == value:
                    pref = value
                    action.setChecked(True)
                self.menubar[item][title] = action
            pref = pref or supaDict[item]['default']
            self.Bakery.setPreference(item, pref)

        default = None
        group = None
        titles = ['Additional setting']
        settings = ['additional']
        uistates = [True] # Whether the setting is disabled or not
        defaults = [False]
        for title, setting, state, uistate in zip(titles, settings, defaults, uistates):
            pref = self.Bakery.getPreference(setting)
            if self.Bakery.getPreference(setting) == None:
                self.Bakery.setPreference(setting, state)
                pref = state
            action = addaction(self.Bakery.setPreference, setting, '')
            action.setChecked(bool(pref))
            action.setDisabled(uistate)
            self.menubar['Export'][setting] = action
            menu.addAction(action)

        helpmenu = self.window.menuBar().addAction('Help')
        helpmenu.triggered.connect(self.openDocumentation)

    def createPresetsBar(self):
        """Create the basic elements for the preset bar in the attribute Layout with the help of the RowLayout class"""
        for mode in self.convertMode:
            self.interface[mode]['presets'] = RowLayout(self.centralwidget)
            self.interface[mode]['presets'].addLabel('Presets')
            self.interface[mode]['presets'].addCombobox()
            self.interface[mode]['presets'].combobox.activated[str].connect(self.setShaderPreset)
            plus = self.interface[mode]['presets'].addButton('+', 20)
            minus = self.interface[mode]['presets'].addButton('-', 20)
            plus.setFlat(True)
            minus.setFlat(True)
            plus.clicked.connect(lambda: self.addShaderPreset())
            minus.clicked.connect(lambda: self.deleteShaderPreset())
            self.updatePresetsBar(mode)
            self.interface[mode]['presets'].hide()
            self.interface['attributes']['layout'].addLayout(self.interface[mode]['presets'])

    def createUdimsBar(self):
        """Create the basic elements for the preset bar in the attribute Layout with the help of the RowLayout class"""
        for mode in self.convertMode:
            self.interface[mode]['udims'] = RowLayout(self.centralwidget)
            self.interface[mode]['udims'].addLabel('UDIMs')
            self.interface[mode]['udims'].addToolbutton()
            self.interface[mode]['udims'].addSpacer()
            self.interface[mode]['udims'].toolmenu = QtGui.QMenu(self.centralwidget)
            self.interface[mode]['udims'].toolbutton.setMenu(self.interface[mode]['udims'].toolmenu)
            self.interface[mode]['udims'].toolbutton.setPopupMode(QtGui.QToolButton.InstantPopup)
            self.interface[mode]['udims'].hide()
            self.interface['attributes']['layout'].addLayout(self.interface[mode]['udims'])

    def createAttributesLayout(self):
        """Create all the basics elements for the attribute Layout
        It is created automatically through a dict and with the help of the RowLayout class
        """
        attributesRender = {'resolution': {'label': {}, 'field': {'validator': 'int', 'minimum': 1, 'maximum': 65536}, 'spacer': {}},
                            'separator': {'separator': {}}}

        attributes =   {'OCC': {'minSamples': {'label': {}, 'field': {'validator': 'int', 'minimum': 1, 'maximum': 1000}, 'slider': {'mode': 'int', 'minimum': 1, 'maximum': 1000}},
                                'maxSamples': {'label': {}, 'field': {'validator': 'int', 'minimum': 1, 'maximum': 1000}, 'slider': {'mode': 'int', 'minimum': 1, 'maximum': 1000}},
                                'coneAngle': {'label': {}, 'field': {'validator': 'float', 'maximum': 180}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 180}},
                                'maxDistance': {'label': {}, 'field': {'validator': 'float', 'maximum': 1000}, 'spacer': {}},
                                'contrast': {'label': {}, 'field': {'validator': 'float'}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 2}},
                                'scale': {'label': {}, 'field': {'validator': 'float'}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 2}},
                                'selfOcclusion': {'label': {}, 'combobox': {'items': ['Disabled', 'Environment', 'Enabled']}, 'spacer': {}}
                                    },
                        'THICK': {'numberOfRays': {'label': {}, 'field': {'validator': 'int', 'minimum': 1, 'maximum': 1000}, 'slider': {'mode': 'int', 'minimum': 1, 'maximum': 1000}},
                                  'coneAngle': {'label': {}, 'field': {'validator': 'float', 'maximum': 90}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 90}},
                                  'maxDistance': {'label': {}, 'field': {'validator': 'float', 'maximum': 1000}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 1000}},
                                 },
                        'DIRT': {'LeaksOn': {'label': {}, 'checkbox': {}},
                                 'LeaksGlobalScale': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.1, 'maximum': 10}, 'slider': {'mode': 'float', 'minimum': 0.1, 'maximum': 10}},
                                 'LeaksDistance': {'label': {}, 'field': {'validator': 'float', 'minimum': 0, 'maximum': 500}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 500}},
                                 'LeaksGamma': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.01, 'maximum': 10}, 'slider': {'mode': 'float', 'minimum': 0.01, 'maximum': 10}},
                                 'LeaksLacunarity': {'label': {}, 'field': {'validator': 'float', 'minimum': 0, 'maximum': 1}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 1}},
                                 'LeaksLacunarityScale': {'label': {}, 'field': {'validator': 'float', 'minimum': 1, 'maximum': 100}, 'slider': {'mode': 'float', 'minimum': 1, 'maximum': 100}},
                                 'LeaksYmultiplier': {'label': {}, 'field': {'validator': 'float', 'minimum': 1, 'maximum': 10}, 'slider': {'mode': 'float', 'minimum': 1, 'maximum': 10}},
                                 'LeaksYScaleMult': {'label': {}, 'field': {'validator': 'float', 'minimum': 1, 'maximum': 100}, 'slider': {'mode': 'float', 'minimum': 1, 'maximum': 100}},
                                 'LeaksOcclusionScale': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.1, 'maximum': 10}, 'slider': {'mode': 'float', 'minimum': 0.1, 'maximum': 10}},
                                 'ThicknessOn': {'label': {}, 'checkbox': {}},
                                 'ThicknessDistance': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.1, 'maximum': 5}, 'slider': {'mode': 'float', 'minimum': 0.1, 'maximum': 5}},
                                 'OmniDirtOn': {'label': {}, 'checkbox': {}},
                                 'OmniDirtPatternScale': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.2, 'maximum': 20}, 'slider': {'mode': 'float', 'minimum': 0.2, 'maximum': 20}},
                                 'OmniDirtMaxDistance': {'label': {}, 'field': {'validator': 'float', 'minimum': 0, 'maximum': 20}, 'slider': {'mode': 'float', 'minimum': 0, 'maximum': 20}},
                                 'OmniDirtGamma': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.2, 'maximum': 2}, 'slider': {'mode': 'float', 'minimum': 0.2, 'maximum': 2}},
                                 'VertexPaintDirt': {'label': {}, 'checkbox': {}},
                                 'VertexPaintDirtScale': {'label': {}, 'field': {'validator': 'float', 'minimum': 0.2, 'maximum': 4}, 'slider': {'mode': 'float', 'minimum': 0.2, 'maximum': 4}},
                                 'SplitToRGB': {'label': {}, 'checkbox': {}}
                                },
                        'RGB': {},

                            }
        attributesRenderOrder = ['resolution', 'separator']
        self.attributesOrder = {'OCC': ['minSamples', 'maxSamples', 'coneAngle', 'maxDistance', 'contrast', 'scale', 'selfOcclusion'],
                                'THICK': ['numberOfRays', 'coneAngle', 'maxDistance'],
                                'DIRT': ['LeaksOn', 'LeaksGlobalScale', 'LeaksDistance', 'LeaksGamma', 'LeaksLacunarity', 'LeaksLacunarityScale', 'LeaksYmultiplier', 'LeaksYScaleMult', 'LeaksOcclusionScale', 'ThicknessOn', 'ThicknessDistance', 'OmniDirtOn', 'OmniDirtPatternScale', 'OmniDirtMaxDistance', 'OmniDirtGamma', 'VertexPaintDirt', 'VertexPaintDirtScale', 'SplitToRGB'],
                                'RGB': []}
        rowOrder = ['label', 'field', 'slider', 'combobox', 'checkbox', 'spacer', 'separator']

        self.interface['attributes']['spacer'] = QtGui.QSpacerItem(0, 5, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.interface['attributes']['layout'].addItem(self.interface['attributes']['spacer'])

        # create rows automatically
        for mode in attributes:
            attributes[mode].update(attributesRender)
            self.attributesOrder[mode][0:0] = attributesRenderOrder
            for key, value in attributes[mode].iteritems():
                self.interface[mode][key] = RowLayout(self.centralwidget)
                for item in rowOrder:
                    try:
                        getattr(self.interface[mode][key], 'add' + item.capitalize())(**value[item])
                    except KeyError:
                        pass
                if 'field' in value and 'slider' in value:
                    self.interface[mode][key].connectFieldSlider()
                self.interface[mode][key].hide()

            # add to layout
            for elem in self.attributesOrder[mode]:
                self.interface['attributes']['layout'].addLayout(self.interface[mode][elem])
                self.interface[mode][elem].setText([QtGui.QApplication.translate("MainWindow", tdLib.camelCaseSeparator(elem).title(), None, QtGui.QApplication.UnicodeUTF8)])

        self.interface['attributes']['layout'].addItem(self.interface['attributes']['spacer'])

    def updateFinalButtons(self):
        """Update the text of the Preview and Bake buttons depending if there is a shader selected or none, or no shaders in the engine."""
        if self._currentShaderButton:
            self.interface['finalbuttons']['preview'].setText(QtGui.QApplication.translate("MainWindow", "Preview", None, QtGui.QApplication.UnicodeUTF8))
            self.interface['finalbuttons']['bake'].setText(QtGui.QApplication.translate("MainWindow", "Bake", None, QtGui.QApplication.UnicodeUTF8))
        elif self.Bakery.shaders:
            self.interface['finalbuttons']['preview'].setText(QtGui.QApplication.translate("MainWindow", "Preview All", None, QtGui.QApplication.UnicodeUTF8))
            self.interface['finalbuttons']['bake'].setText(QtGui.QApplication.translate("MainWindow", "Bake All", None, QtGui.QApplication.UnicodeUTF8))

        if not self.Bakery.turtle:
            self.interface['finalbuttons']['preview'].setDisabled(True)
            self.interface['finalbuttons']['interactivebake'].setDisabled(True)
        if not self.Bakery.shaders:
            self.interface['finalbuttons']['preview'].setDisabled(True)
            self.interface['finalbuttons']['interactivebake'].setDisabled(True)
            self.interface['finalbuttons']['bake'].setDisabled(True)
        else:
            self.interface['finalbuttons']['preview'].setDisabled(False)
            self.interface['finalbuttons']['interactivebake'].setDisabled(False)
            self.interface['finalbuttons']['bake'].setDisabled(False)

    def updateAttributesLayout(self, mode):
        """Hide attributes of the old mode and show the new activated mode."""
        try:
            for elem in self.attributesOrder[self.mode]:
                self.interface[self.mode][elem].hide()
            self.interface[self.mode]['presets'].hide()
            self.interface[self.mode]['udims'].hide()
            for elem in self.attributesOrder[mode]:
                self.interface[mode][elem].show()
            self.interface[mode]['presets'].show()
            self.interface[mode]['udims'].show()
            self.mode = mode
        except KeyError:
            pass

    def addShadersToUI(self, shaders):
        self.interface['shaders']['layout'].removeItem(self.interface['shaders']['spacer'])
        for shader in shaders:
            self.shaders[shader] = self.createShaderLayout(shader)
            self.interface['shaders']['layout'].addLayout(self.shaders[shader]['layout'])
        self.interface['shaders']['layout'].addItem(self.interface['shaders']['spacer'])

    def removeShadersFromUI(self, shaders):
        """Not used"""
        for shader in shaders:
            for i in iter(functools.partial(self.shaders[shader]['layout'].takeAt, 0), None):
                w = i.widget().deleteLater()
                w = None

    def addShaders(self, mode):
        """Add every shaders selected with the engine, and add them to the UI.
        Do a copy of all the attributes if a shader is selected and you are adding shaders in the same mode.
        """
        def copyAttributes():
            if current and current.shader.mode == mode:
                for shader in shaders:
                    shader.renderAttr = current.shader.renderAttr.copy()
                    shader.shaderAttr = current.shader.shaderAttr.copy()

        current = self._currentShaderButton
        self.saveCurrentShader(uncheck=False)
        shaders = self.Bakery.addShaders(mode)
        copyAttributes()
        self.addShadersToUI(shaders)
        try:
            self.shaders[shaders[-1]]['button'].click()
        except IndexError:
            logger.warning("There isn't any mesh or shaders in your selection.")
        # self._currentShaderButton = self.shaders[shader]['button']
        self.resize()

    def deleteShader(self, shader):
        """Remove the shader from the engine and remove the layout in the UI."""
        self.saveCurrentShader()
        self.Bakery.removeShader(shader)
        for i in iter(functools.partial(self.shaders[shader]['layout'].takeAt, 0), None):
            w = i.widget().deleteLater()
            w = None
        del self.shaders[shader]
        self.updateFinalButtons()
        self.resize()

    def cleanShaders(self):
        """Remove every shaders from the interface and the engine."""
        for shader in list(self.Bakery.shaders):
            self.deleteShader(shader)

    def createShaderLayout(self, shader):
        """Create the layout/label/field/button of the shader"""
        tooltip = "The final name of the file.\nDon't forget to replace this if you have the same shaders several times in the same mode, otherwise it will overwrite the file over and over."
        colors = {'OCC': '#317531', 'THICK': '#a50', 'DIRT': '#05a', 'RGB': '#B73D66' }
        layout = QtGui.QHBoxLayout()
        button = QtGui.QPushButton(self.centralwidget)
        button.shader = shader # Save the shader in the button to be able to accesss it easily elsewhere
        button.setFlat(True)
        button.setText(shader.mode)
        button.setCheckable(True)
        button.setMinimumWidth(40)
        button.clicked.connect(lambda: self.changeCurrentShader(button))
        button.setStyleSheet('background-color: {}'.format(colors[shader.mode]))
        self.window.setStyleSheet("QPushButton:checked {border:none;padding:4px}");
        self.updateShaderTooltip(button)
        self.interface['shaders']['buttonGroup'].addButton(button)
        field = QtGui.QLineEdit(self.centralwidget)
        field.setText(shader.fileName)
        field.textChanged.connect(shader.setFilename)
        field.setToolTip(tooltip)
        field.setStatusTip(tooltip)
        delete = QtGui.QPushButton(self.centralwidget)
        delete.clicked.connect(lambda: self.deleteShader(shader))
        delete.setText(' X ')
        delete.setFlat(True)
        delete.setStyleSheet('background-color: #a00;color:#f00')
        layout.setSpacing(0)
        layout.addWidget(button)
        layout.addWidget(field)
        layout.addWidget(delete)

        # Add right click menu on the shader button for copy paste
        button.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        copyAttr = QtGui.QAction(button)
        pasteAttr = QtGui.QAction(button)
        copyAttr.setText('Copy')
        pasteAttr.setText('Paste')
        copyAttr.triggered.connect(functools.partial(self.copyAttributes, shader))
        pasteAttr.triggered.connect(functools.partial(self.pasteAttributes, button))
        button.addAction(copyAttr)
        button.addAction(pasteAttr)

        for widget in [button, field, delete]: # Configure and run the animation
            effect = QtGui.QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            ag = QtCore.QSequentialAnimationGroup(widget)
            anim = fade(effect, 1000)
            ag.addAnimation(anim)
            ag.start()
        return {'layout': layout, 'button': button, 'field': field, 'delete': delete}

    def copyAttributes(self, shader):
        self.copyAttributes = shader.shaderAttr.copy()

    def pasteAttributes(self, button):
        if sorted(button.shader.shaderAttr) == sorted(self.copyAttributes):
            button.shader.shaderAttr = self.copyAttributes
            self.updateShaderTooltip(button)

    def saveCurrentShader(self, uncheck=True):
        """Save the shader attributes in the Bakery engine
        Update the tooltip on the shader button with its shader attributes
        Uncheck the shader if the argument says so, and remove the attributes layout."""
        if self._currentShaderButton:
            self.updateShaderTooltip(self._currentShaderButton)
            self.setShaderAttributes(self._currentShaderButton.shader)
            if uncheck:
                self.updateAttributesLayout(self._currentShaderButton.shader.mode)
                self._currentShaderButton.setChecked(False)
                self._currentShaderButton = None
                self.updateAttributesLayout(None)

    def changeCurrentShader(self, button):
        """Used when the user click on a shader button in the shader list"""
        self.saveCurrentShader()
        self.Bakery.toBake = []
        current = self.interface['shaders']['buttonGroup'].checkedButton()
        if current:
            self.Bakery.toBake = [button.shader]
            self.updateAttributesLayout(button.shader.mode)
            self._currentShaderButton = current
            self.updateUdimsBar()
            self.getShaderAttributes(button.shader)
        self.updateFinalButtons()
        self.resize()

    def updateShaderTooltip(self, button):
        """Update the tooltip of the shader with the shader attributes."""
        tip = 'Nb UDIMs: {} / {}\n\n'.format(len(button.shader.udims), len(button.shader.udimsTotal))
        tip += 'resolution: {}\n'.format(button.shader.renderAttr['resolution'])
        for key, value in button.shader.shaderAttr.iteritems():
            tip += '{}: {}\n'.format(key, value)
        button.setToolTip(tip.strip())

    def getShaderAttributes(self, shader=None):
        """Set the shader values in the UI from the engine values."""
        self.interface[shader.mode]['resolution'].setValue([shader.renderAttr['resolution']])
        for key, value in shader.shaderAttr.iteritems():
            rowlayout = self.interface[shader.mode][key]
            rowlayout.setValue([value])
            rowlayout.setItem([value])

    def setShaderAttributes(self, shader):
        """Update the shader attributes in the engine from the values set in the UI."""
        shader.renderAttr['resolution'] = int(self.interface[shader.mode]['resolution'].getValue()[0])
        for attr in shader.shaderAttr:
            shader.shaderAttr[attr] = self.interface[shader.mode][attr].getValue()[0]

    def getDefaultShaderAttributes(self):
        """Set default attributes values in the UI."""
        self.interface[self.mode]['resolution'].setValue([self.Bakery.renderAttr['resolution']])
        shaderAttr = self.Bakery.shaderAttr[self.mode]
        for key, value in shaderAttr.iteritems():
            rowlayout = self.interface[self.mode][key]
            rowlayout.setValue([value])
            rowlayout.setItem([value])

    def toggleUdimState(self, udim):
        try:
            self._currentShaderButton.shader.udims.remove(udim)
        except ValueError:
            self._currentShaderButton.shader.udims.append(udim)
        self.updateUdimsBar()

    def updateUdimsBar(self):
        """Get all the UDIM of the shader and put them in the ToolButton in the right state."""
        udims = self._currentShaderButton.shader.udims
        udimsTotal = self._currentShaderButton.shader.udimsTotal
        self.interface[self.mode]['udims'].toolmenu.clear()
        self.interface[self.mode]['udims'].toolbutton.setText('  {}  /  {}   '.format(len(udims), len(udimsTotal)))
        for udim in udimsTotal:
                action = self.interface[self.mode]['udims'].toolmenu.addAction('10{}{}'.format(udim[1], udim[0] + 1))
                action.triggered.connect(functools.partial(self.toggleUdimState, udim))
                action.setCheckable(True)
                action.setChecked(udim in udims)

    def updatePresetsBar(self, mode):
        """Get all the presets saved in the settings and put them in the combobox."""
        self.interface[mode]['presets'].combobox.clear()
        for item in self.listShaderPresets()[mode]:
            self.interface[mode]['presets'].combobox.addItem(item)

    def setShaderPreset(self):
        """Set the shader attributes when a preset is activated."""
        preset = self.interface[self.mode]['presets'].combobox.currentText()
        if preset == 'Default':
            self.getDefaultShaderAttributes()
        else:
            preset = self.mode + '/' + preset
            shaderAttr = self.settings.value(preset)
            self._currentShaderButton.shader.shaderAttr = shaderAttr
            self.getShaderAttributes(self._currentShaderButton.shader)

    def addShaderPreset(self):
        """Save the current shader attributes to the settings."""
        self.saveCurrentShader(uncheck=False)
        text, ok = QtGui.QInputDialog.getText(self.centralwidget, 'Preset Name', 'Enter the name of the preset:')
        if ok and text:
            preset = text
            shaderAttr = self.settings.setValue(self.mode + '/' + preset, self._currentShaderButton.shader.shaderAttr)
            self.updatePresetsBar(self.mode)
            index = self.interface[self.mode]['presets'].combobox.findText(preset)
            self.interface[self.mode]['presets'].combobox.setCurrentIndex(index)

    def deleteShaderPreset(self):
        """Delete the current preset from the settings."""
        preset = self.interface[self.mode]['presets'].combobox.currentText()
        if preset == 'Default':
            pass
        else:
            preset = self.mode + '/' + preset
            self.settings.remove(preset)
            self.updatePresetsBar(self.mode)

    def listShaderPresets(self):
        """List all the presets in all different modes"""
        result = {}
        for mode in self.convertMode:
            result[mode] = [i.split('/', 1)[-1] for i in self.settings.allKeys() if i.startswith(mode)]
            result[mode][:0] = ['Default']
        return result

    def bake(self):
        """Tell the engine to bake the shaders"""
        if self.Bakery.shaders:
            self.saveCurrentShader(uncheck=False)
            b.initstats.emit('bake')
            self.Bakery.sendBatch()
            effect = QtGui.QGraphicsColorizeEffect(self.interface['finalbuttons']['bake'])
            self.interface['finalbuttons']['bake'].setGraphicsEffect(effect)
            ag = QtCore.QSequentialAnimationGroup(self.interface['finalbuttons']['bake'])
            anim = fade(effect, 1000, 'color', QtGui.QColor(0, 255, 0, 200), QtGui.QColor(0, 255, 0, 0))
            ag.addAnimation(anim)
            ag.start()
        self.resize()

    def preview(self):
        """Call a preview of the selected shader, or every shaders if none are selected."""
        self.saveCurrentShader(uncheck=False)
        t = b.initstats.emit('preview', True)
        try:
            self.Bakery.preview([self._currentShaderButton.shader])
        except AttributeError:
            self.Bakery.preview(self.Bakery.shaders)
        t.stop()
        self.resize()

    def bakeInteractive(self):
        """Do the bake interactively."""
        self.Bakery.executeMayabatch()


    def render(self):
        """Do a preview render with the current camera instead of a usual bake. The result can be slightly different than the final bake"""
        self.saveCurrentShader(uncheck=False)
        t = b.initstats.emit('render', True)
        try:
            self.Bakery.render(self._currentShaderButton.shader)
        except AttributeError:
            self.Bakery.render()
        t.stop()

    def resize(self):
        """Call a render, obsolete since this seems to be managed by the engine automatically."""
        cur = self.window.width()
        min = self.window.minimumWidth()
        self.window.setMinimumWidth(cur)
        self.interface['shaders']['layout'].activate()
        self.verticalLayout.activate()
        self.window.adjustSize()
        self.window.setMinimumWidth(min)

    def retranslateUi(self):
        """Change some text in the UI."""
        self.window.setWindowTitle(QtGui.QApplication.translate("MainWindow", "The Bakery", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['maintabs']['occlusion'].setText(QtGui.QApplication.translate("MainWindow", "Occlusion", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['maintabs']['thickness'].setText(QtGui.QApplication.translate("MainWindow", "Thickness", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['maintabs']['dirt'].setText(QtGui.QApplication.translate("MainWindow", "Dirt", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['maintabs']['rgb'].setText(QtGui.QApplication.translate("MainWindow", "Rgb", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['finalbuttons']['preview'].setText(QtGui.QApplication.translate("MainWindow", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['finalbuttons']['bake'].setText(QtGui.QApplication.translate("MainWindow", "Bake", None, QtGui.QApplication.UnicodeUTF8))
        self.interface['finalbuttons']['interactivebake'].setText(u"\u21CB")

    def createTooltips(self):
        """Create all the tooltips on the different part of the UI."""
        presetTips = 'Change the Anti-aliasing settings, for more information see the documentation.'
        tipsDict = {
            self.menubar['Preset']['Draft']: presetTips,
            self.menubar['Preset']['Low']: presetTips,
            self.menubar['Preset']['Medium']: presetTips,
            self.menubar['Preset']['High']: presetTips,
            self.menubar['Preset']['Very High']: presetTips,
            self.menubar['Preview']['Render']: 'It will do a render instead of an interactive bake.\nIt may be different than the final bake.',
            self.menubar['Export']['Auto']: 'Export only what is needed OR everything if there is an OCC shader.',
            self.menubar['Export']['Open Original Scene']: 'Open the original scene.\nIt will not take into account anything you changed in the scene unless you saved it.',
            self.menubar['Export']['Force All']: 'Force the export of everything in the scene.',
            self.menubar['Export']['Selection']: 'Force the selection of only what is actually selected.',
            self.interface['maintabs']['occlusion']: 'Add the selected shaders to bake an occlusion map.',
            self.interface['maintabs']['thickness']: 'Add the selected shaders to bake a thickness map.',
            self.interface['maintabs']['dirt']: 'Add the selected shaders to bake a dirt map.\nThe omni directional dirt is based on ambient occlusion and adds grime in all recessed areas.',
            self.interface['finalbuttons']['preview']: 'Create a preview bake with a smaller resolution of:\n - the selected shader,\n - or all the shaders if none are selected.',
            self.interface['finalbuttons']['interactivebake']: 'Bake the textures in this session of Maya instead of a deported batch.\nIt will either bake the selected shader, or all the shaders if none are selected.',
            self.interface['finalbuttons']['bake']: 'Send the shader(s) to bake.\nYou will receive an email with the result and link(s) to the file(s).',

            self.interface['OCC']['resolution']: 'Resolution of the final map.',
            self.interface['OCC']['minSamples']: 'Minimum number of rays used for the sampling of occlusion.',
            self.interface['OCC']['maxSamples']: 'Maximum number of rays used for the sampling of occlusion.',
            self.interface['OCC']['coneAngle']: 'Set the angle cone used to sample the occlusion contact zone.\n180 represents covers an entire hemisphere.',
            self.interface['OCC']['maxDistance']: 'Distance beyond which the occlusion is no longer evaluated.\nIf set to 0 the engine will automatically set it depending on the scale of the scene.',
            self.interface['OCC']['contrast']: 'Contrast of the ambient occlusion.',
            self.interface['OCC']['scale']: 'Accentuates the effect of the occlusion.',
            self.interface['OCC']['selfOcclusion']: ' - Disabled: Objects does not cast occlusion on itself.\n - Environment: Hits on the same objects are treated as misses, i.e the ray is terminated and the environment is set.\n - Enabled: Objects occludes themselves normally. ',

            self.interface['THICK']['resolution']: 'Resolution of the final map.',
            self.interface['THICK']['numberOfRays']: 'Number of rays used for the sampling of the thickness.',
            self.interface['THICK']['coneAngle']: 'Set the angle cone used to sample the occlusion contact zone.\n180 represents covers an entire hemisphere.',
            self.interface['THICK']['maxDistance']: 'Distance beyond which the thickness is no longer evaluated.',

            self.interface['DIRT']['resolution']: 'Resolution of the final map.',
            self.interface['DIRT']['OmniDirtMaxDistance']: 'Distance beyond which the omni directional dirt is no longer evaluated.',
            self.interface['DIRT']['OmniDirtPatternScale']: 'Scale of the noise fractal used in the omnidirectional dirt.',
            self.interface['DIRT']['OmniDirtGamma']: 'Accentuates the effect of the omnidirectional dirt.',
            self.interface['DIRT']['LeaksDistance']: 'Distance beyond which the drips disappear.',
            self.interface['DIRT']['LeaksLacunarityScale']: 'Scale of the noise fractal used in the drips.',
            self.interface['DIRT']['LeaksGamma']: 'Accentuates the effect of drips.',
            # self.interface['DIRT']['CornerMaxDistance']: 'Distance beyond which the corners are not marked.',
            self.interface['DIRT']['VertexPaintDirt']: 'Enables the possibility to manually define areas of dirt using the vertex tool paint by painting dirty areas has black on white.',
            self.interface['DIRT']['VertexPaintDirtScale']: 'Scale of the noise fractal used in the vertex dirt.',
            self.interface['DIRT']['SplitToRGB']: 'Separates the three components of the dirt (Omni Directional and Corner) on all three channels RGB.',
            # self.interface['DIRT']['TopBottomThreshold']: 'On areas whose normal pointing zenith, set the slope on which the dirt will be applied.'
            self.interface['RGB']['resolution']: 'Resolution of the final map.',
            }
        for obj, tip in tipsDict.iteritems():
            obj.setToolTip(tip)
            obj.setStatusTip(tip)

    def openDocumentation(self):
        """Open a browser directly on the documentation."""
        webbrowser.open('http://yourdocumentation.com')

    def closeEvent(self, event):
        self.saveCurrentShader()
        QtGui.QMainWindow.closeEvent(self.window, event)


def fade(target, duration, propertyName='opacity', start=0, end=1, easingCurve=QtCore.QEasingCurve.OutCirc):
    """Get animation to fade in the image
    :param target: Target property of animation(QGraphicsOpacityEffect)
    :param duration: Time spent on animation
    :param propertyName: Name of the property changed
    :param start: Start value of the effect
    :param end: End value of the effect
    :param easingCurve: Type of animation curve
    """
    an = QtCore.QPropertyAnimation(target, propertyName)
    an.setDuration(duration)
    an.setStartValue(start)
    an.setEndValue(end)
    an.setEasingCurve(easingCurve)
    return an


def launch_ui():
    MainWindow = qtwrapper.get_maya_window()
    Bakery = b.Bakery()
    gui = BakeryUI(MainWindow, Bakery)
    gui.setupUi()
    gui.window.show()
    return gui

if __name__ == '__main__':
    gui = launch_ui()
