import time

cmds.dockControl('Script Editor', area='right', content='scriptEditorPanel1Window')


minus = cmds.playbackOptions(query=True, minTime=True)
maxus = cmds.playbackOptions(query=True, maxTime=True)

def getaverageframerate(minus, maxus):
    frames = range(int(minus), int(maxus))
    elapsed = []
    for i in frames:
        cmds.currentTime(i - 1)
        break
    for i in frames:
        t = time.time()
        cmds.currentTime(i)
        elapsed.append(time.time() - t)
    framerates = [1/i for i in elapsed]
    average = sum(framerates) / float(len(framerates))
    return average


def getdefaultpreferences():
    """Use only at first launch of maya."""
    platform = cmds.about(operatingSystem=True)
    version = cmds.about(installedVersion=True).replace(' ', '')
    for i in cmds.optionVar(list=True):
        value = cmds.optionVar(query=i)
        if isinstance(value, basestring):
            value = '"' + value + '"'
        print '"{0}": {1},'.format(i, value)

    print version + '-' + platform + '-optionvars.json'


import mgmaya.mgQt as mgQt
MainWindow = mgQt.getMayaMainWindow()
MainWindow.setStyleSheet('background-image:url(path/glitchy2.png)')


import profiler
profiler.PyStart()
profiler.PyStop()
profiler.PyStop("/tmp/prof", False)


# # User Can Manage Levels Through The Maya Logging Menu - This is how you enable it
from pymel.tools import loggingControl
loggingControl.initMenu()





