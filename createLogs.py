import os
import time
import maya.cmds as cmds

def createLogs(listUsers=[]):
    """
    Creates a log file in the maya prefs folder, recording everything printed in the Command File Output
    If nothing is specified for the argument 'listUser', it will do it for everyone
    """
    userLogin  = os.environ['USER']
    if userLogin in listUsers or not listUsers:
        mayaVersion = cmds.about( version=True )
        yearMonth   = time.strftime( '%Y-%m' )
        timeNow     = time.strftime( '%Y-%m-%d__%H:%M:%S' )
        fileName    = timeNow + '.log'
        folderPath  = os.path.join( os.environ['MAYA_APP_DIR'], 'mayalogs', mayaVersion.replace(' ', '-'), yearMonth )
        filePath    = os.path.join( folderPath, fileName )

        try:
            os.makedirs( folderPath )
        except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

        cmds.cmdFileOutput( open=filePath )
