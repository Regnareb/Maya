import maya.cmds as cmds

class td_OptionsWindow(object):
    """A base class for an options window"""

    @classmethod
    def showUI(cls):
        """A function to instantiate the options window"""
        win = cls()
        win.create()
        return win

    def __init__(self):
        """Initialize common data attributes"""
        # unique window handle
        self.window = 'td_optionsWindow'
        # window title
        self.title = 'Options Window'
        # window size
        self.size = (546, 350)
        # specify whether the 'Save Settings' command is supported
        self.supportsSaveSettings = False
        # specify whether the tool/action toggle is supported
        self.supportsToolAction = False
        # name to display on the action button
        self.actionName = 'Apply and Close'

    def create(self):
        """Draw the window"""
        # delete the window if its handle exists
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        # initialize the window
        self.window = cmds.window(
            self.window,
            title=self.title,
            widthHeight=self.size,
            menuBar=True
        )
        # main form for the window
        self.mainForm = cmds.formLayout(nd=100)
        # create common menu items and buttons
        self.commonMenu()
        self.commonButtons()
        # see getOptionBox.mel for why we implement this layout pattern to emulate Maya's option boxes
        self.optionsBorder = cmds.tabLayout(
            scrollable=True,
            tabsVisible=False,
            height=1,
            childResizable=True
        )
        cmds.formLayout(
            self.mainForm, e=True,
            attachForm=(
                [self.optionsBorder,'top',0],
                [self.optionsBorder,'left',2],
                [self.optionsBorder,'right',2]
            ),
            attachControl=(
                [self.optionsBorder,'bottom',5,self.applyBtn]
            )
        )
        # form to attach controls in displayOptions()
        self.optionsForm = cmds.formLayout(nd=100)
        self.displayOptions()
        # show the window
        cmds.showWindow()

    def commonMenu(self):
        """Create common menu items for all option boxes"""
        self.editMenu = cmds.menu(label='Edit')
        self.editMenuSave = cmds.menuItem(
            label='Save Settings',
            enable=self.supportsSaveSettings,
            command=self.editMenuSaveCmd
        )
        self.editMenuReset = cmds.menuItem(
            label='Reset Settings',
            command=self.editMenuResetCmd
        )
        self.editMenuDiv = cmds.menuItem(d=True)
        self.editMenuRadio = cmds.radioMenuItemCollection()
        self.editMenuTool = cmds.menuItem(
            label='As Tool',
            radioButton=True,
            enable=self.supportsToolAction,
            command=self.editMenuToolCmd
        )
        self.editMenuAction = cmds.menuItem(
            label='As Action',
            radioButton=True,
            enable=self.supportsToolAction,
            command=self.editMenuActionCmd
        )
        self.helpMenu = cmds.menu(label='Help')
        self.helpMenuItem = cmds.menuItem(
            label='Help on %s'%self.title,
            command=self.helpMenuCmd
        )

    def helpMenuCmd(self, *args):
        """Override this method to display custom help"""
        pass

    def editMenuSaveCmd(self, *args):
        """Override this method to implement Save Settings"""
        pass

    def editMenuResetCmd(self, *args):
        """Override this method to implement Reset Settings"""
        pass

    def editMenuToolCmd(self, *args):
        """Override this method to implement tool mode"""
        pass

    def editMenuActionCmd(self, *args):
        """Override this method to implement action mode"""
        pass

    def actionBtnCmd(self, *args):
        """Apply actions and close window"""
        self.applyBtnCmd()
        self.closeBtnCmd()

    def applyBtnCmd(self, *args):
        """Override this method to apply actions"""
        pass

    def closeBtnCmd(self, *args):
        """Close window"""
        cmds.deleteUI(self.window, window=True)

    def commonButtons(self):
        """Create common buttons for all option boxes"""
        self.commonBtnSize = ((self.size[0]-18)/3, 26)
        self.actionBtn = cmds.button(
            label=self.actionName,
            height=self.commonBtnSize[1],
            command=self.actionBtnCmd
        )
        self.applyBtn = cmds.button(
            label='Apply',
            height=self.commonBtnSize[1],
            command=self.applyBtnCmd
        )
        self.closeBtn = cmds.button(
            label='Close',
            height=self.commonBtnSize[1],
            command=self.closeBtnCmd
        )
        cmds.formLayout(
            self.mainForm, e=True,
            attachForm=(
                [self.actionBtn,'left',5],
                [self.actionBtn,'bottom',5],
                [self.applyBtn,'bottom',5],
                [self.closeBtn,'bottom',5],
                [self.closeBtn,'right',5]
            ),
            attachPosition=(
                [self.actionBtn,'right',1,33],
                [self.closeBtn,'left',0,67]
            ),
            attachControl=(
                [self.applyBtn,'left',4,self.actionBtn],
                [self.applyBtn,'right',4,self.closeBtn]
            ),
            attachNone=(
                [self.actionBtn,'top'],
                [self.applyBtn,'top'],
                [self.closeBtn,'top']
            )
        )

    def displayOptions(self):
        """Override this method to display options controls"""
        pass
