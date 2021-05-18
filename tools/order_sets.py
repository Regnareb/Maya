import re
import logging
import functools
import shiboken2
import maya.cmds as cmds
import maya.OpenMayaUI as mui
from PySide2 import QtCore, QtWidgets, QtGui

logger = logging.getLogger(__name__)


class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.Signal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()


class MayaWindow(QtWidgets.QMainWindow, object):
    def __init__(self, mainwindow):
        super(MayaWindow, self).__init__(parent=mainwindow)
        self.title = 'Sort Sets'
        self.setWindowTitle(self.title)
        self.setObjectName(self.title)
        self.setProperty("saveWindowPref", True)  # If setObjectName is set, Maya will remember pos and size of window
        self.create_ui()

    def block_signals(function, *args, **kwargs):
        """Decorator that blocks all Qt signals at once when modifying the UI"""
        @functools.wraps(function)
        def wrapper(self):
            try:
                for i in self.interface.values():
                    i.blockSignals(True)
                function(self, *args, **kwargs)
            finally:
                for i in self.interface.values():
                    i.blockSignals(False)
        return wrapper

    def create_ui(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.layoutv = QtWidgets.QVBoxLayout(self.centralwidget)
        self.interface = {}
        self.interface['select_set'] = ComboBox()
        self.interface['select_set'].setView(QtWidgets.QListView())
        self.interface['set_elements'] = QtWidgets.QListWidget()
        self.interface['set_elements'].setDragEnabled(True)
        # self.interface['set_elements'].setSelectionMode(QtWidgets.QTableWidget.ExtendedSelection)
        self.interface['set_elements'].setDragDropMode(QtWidgets.QTableWidget.InternalMove)
        # self.interface['set_elements'].setDragDropOverwriteMode(True)  # Removes the original item after moving instead of clearing it
        self.interface['button_sort'] = QtWidgets.QPushButton('Sort Elements')
        self.interface['menu_sort'] = QtWidgets.QMenu(parent=self.interface['button_sort'])
        action = QtWidgets.QAction(QtGui.QIcon(':/sortName.png'), 'Natural Sort', self)
        action.triggered.connect(functools.partial(self.sort, True))
        self.interface['menu_sort'].addAction(action)
        action = QtWidgets.QAction(QtGui.QIcon(':/reverseOrder.png'), 'Reversed', self)
        action.triggered.connect(functools.partial(self.sort, False))
        self.interface['menu_sort'].addAction(action)
        self.interface['button_sort'].setMenu(self.interface['menu_sort'])
        self.layoutv.addWidget(self.interface['select_set'])
        self.layoutv.addWidget(self.interface['set_elements'])
        self.layoutv.addWidget(self.interface['button_sort'])
        self.setCentralWidget(self.centralwidget)
        self.interface['menu_sort'].aboutToShow.connect(self.set_menuwidth)
        self.interface['select_set'].popupAboutToBeShown.connect(self.get_sets)
        self.interface['select_set'].currentIndexChanged.connect(self.get_set_elements)
        self.interface['set_elements'].model().rowsMoved.connect(self.apply_order)
        self.show()
        self.interface['button_sort'].setMaximumHeight(self.interface['select_set'].size().height())
        self.interface['select_set'].setStyleSheet("QListView::item {{height: {}px;}}".format(self.interface['select_set'].size().height()))

    def sort(self, order):
        """Sort the elements automatically"""
        items = [self.interface['set_elements'].item(x).text() for x in range(self.interface['set_elements'].count())]
        items = natural_sort(items)
        if not order:
            items.reverse()
        self.interface['set_elements'].clear()
        self.interface['set_elements'].addItems(items)
        self.apply_order()

    def set_menuwidth(self):
        """Apply the same width for QPushButton and Qmenu"""
        self.interface['menu_sort'].setMinimumWidth(self.interface['button_sort'].width())
        self.interface['menu_sort'].setMaximumWidth(self.interface['button_sort'].width())

    @block_signals
    def get_sets(self):
        """Get all sets in the scene and add them to the UI"""
        self.sets = list(set(cmds.ls(exactType='objectSet')) - set(['defaultLightSet', 'defaultObjectSet']))
        self.sets.sort()
        self.interface['select_set'].clear()
        self.interface['select_set'].addItems(self.sets)
        self.interface['select_set'].setCurrentIndex(-1)
        if not self.sets:  # In case there are no more sets in the scene
            self.setWindowTitle(self.title)
            self.interface['set_elements'].clear()

    @block_signals
    def get_set_elements(self):
        """Get the connected nodes of the corresponding set and add them to the UI"""
        objectset = self.interface['select_set'].currentText()
        self.interface['set_elements'].clear()
        if not objectset or not cmds.ls(objectset, type='objectSet'):
            logger.error("Couldn't find according set. Reselect one.") if objectset else ''
            self.interface['select_set'].setCurrentIndex(-1)
            return
        elements = cmds.listConnections(objectset + '.dagSetMembers') or []
        self.interface['set_elements'].addItems(elements)
        self.setWindowTitle('{} ({}) '.format(self.title, len(elements)))

    def apply_order(self):
        """Apply the order of elements in the UI to the set in the scene"""
        with UndoContext(catch_exception=True, undo_at_exception=True):
            objectset = self.interface['select_set'].currentText()
            items = [self.interface['set_elements'].item(x).text() for x in range(self.interface['set_elements'].count())]
            items = [i for i in items if i]
            cmds.sets(clear=objectset)
            for item in items:
                cmds.sets(item, addElement=objectset)
        self.get_set_elements()


def launch_ui():
    mainwindow = get_maya_window()
    gui = MayaWindow(mainwindow)
    return gui


def get_maya_window():
    """Get the maya main window as a QMainWindow instance"""
    ptr = mui.MQtUtil.mainWindow()
    try:
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
    except NameError:
        return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)


def natural_sort(items):
    """Correctly sort a list of string with numeric values"""
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(items, key=alphanum_key)


class UndoContext(object):
    def __init__(self, catch_exception=False, undo_at_exception=False):
        self.catch_exception = catch_exception
        self.undo_at_exception = undo_at_exception

    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        if self.undo_at_exception:
            #  Trigger a command in case because it may undo an operation made by the user
            # if the script raises an exception before any other Maya operation is done
            cmds.currentTime(cmds.currentTime(query=True))

    def __exit__(self, exception_type, exception_value, traceback):
        cmds.undoInfo(closeChunk=True)
        if exception_type and self.undo_at_exception:
            cmds.undo()
        if self.catch_exception:
            return True


if __name__ == "__main__":
    win = launch_ui()
