import os
import time
import maya.cmds as cmds

def createLogs():
    """
    Creates a log file in the maya prefs folder recording everything printed in the Command File Output.
    """
    mayaVersion     = cmds.about( version=True )
    folderYearMonth = time.strftime( '%Y-%m' )
    timeNow         = time.strftime( '%Y-%m-%d__%H:%M:%S' )
    fileName        = timeNow + '.log'
    folderPath      = os.path.join( os.environ['MAYA_APP_DIR'], 'mayalogs', mayaVersion.replace(' ', '-'), folderYearMonth )
    filePath         = os.path.join( folderPath, fileName )

    try:
        os.makedirs( folderPath )
    except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    cmds.cmdFileOutput( open=filePath )
