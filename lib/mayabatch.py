"""
Create a thread with a 'mayabatch' subprocess in it. Sending a path to the Maya scene to open
It unpickle a pickle file in the same path of the Maya file, and execute its 'executeMayabatch' method.
This way MentalRay is imported only outside of production for creating textures, and never screw the official scenes.
"""
import os
import uuid
import atexit
import logging
import threading
import subprocess
import pymel.core as pmc
import lib_pmc as libb
import tdMail
logger = logging.getLogger(__name__)

__version__ = "1.3.0"
__author__  = 'regnareb'


class Mayabatch(threading.Thread):
    instances = []

    def __init__(self, objectRecorded='', mentalRay=False, block=False, mailEnabled=False, mailOnlyCrash=False):
        super(Mayabatch, self).__init__()
        Mayabatch.instances.append( self )
        self.__initialized  = True
        self.objectRecorded = objectRecorded
        self.mentalRay      = mentalRay
        self.mailEnabled    = mailEnabled
        self.mailOnlyCrash  = mailOnlyCrash
        # self.name           = pathSceneTMP
        # self.pathSceneTMP   = pathSceneTMP
        self._stop          = threading.Event()
        atexit.register( self.stop )
        # self.setDaemon(True)
        self.start()
        if block: self.join()


    def __repr__(self):
        r = super(Mayabatch, self).__repr__()
        if self.exitcode:
            r = r.replace( 'stopped', 'crashed' )
        return r


    def run(self):
        nbrCrash      = 0
        self.exitcode = True
        while self.exitcode != 0:
            callPython         = 'callPython "td.maya.lib.mayabatch" "mayabatchExecution" { "%s", "%s" }' % ( self.pathSceneTMP, self.mentalRay )
            ARGS               = ['mayabatch', '-command', callPython]
            self.maya          = subprocess.Popen( ARGS,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   env=self.getEnvironment() )
            self.out, self.err = self.maya.communicate()
            self.exitcode      = self.maya.returncode
            nbrCrash += 1
            if nbrCrash == 3:
                break
        self.returnSignal()
        if self.mailEnabled: self.sendMail()
        self.stop()


    def stop(self):
        self._stop.set()


    def stopped(self):
        return self._stop.isSet()


    def returnSignal(self):
        if self.exitcode != 0:
            logger.debug( self.out )
            logger.error( 'Error in thread: %s' % ( self.err ) )
        else:
            self.result = self.out.splitlines()[-1]
            logger.info( '%s' % ( self.result ) )


    def saveState(self):
        self.pathSceneTMP = pmc.system.Path( libb.saveAsCopy( suffix=uuid.uuid4().hex )
        pathPickle   = str( self.pathSceneTMP ).replace( self.pathSceneTMP.ext, '.pickle')
        libb.pickleObject( pathPickle, self.objectRecorded )



    def sendMail(self):
        user        = os.environ['USER']
        destination = user + '@domain.com'
        subject     = '%s batch result' % (self.mailEnabled [0])
        message     = ''
        message += '%s<br />' % (self.mailEnabled [1])
        if self.exitcode !=0:
            message += '<b style="color:red">Crashed: </b><br />' + self.err.replace('\n', '<br />') + '<br /><br /><b style="color:red">Log:</b><br /> ' + self.out.replace('\n', '<br />') + '<br />'
        else:
            message += '<b style="color:green">Success:</b> ' + self.result.replace('\n', '<br />') + '<br />'

        if self.mailOnlyCrash and self.exitcode !=0 or not self.mailOnlyCrash:
            tdMail.sendHtmlMail('username@domain.com', [destination], subject, message)



    def getEnvironment(self):
        environment = os.environ.copy()
        if self.mentalRay:
            path = os.path.join( os.environ['MAYA_LOCATION'], 'mentalray' )
            if os.path.exists( path ):
                environment['MAYA_MODULE_PATH'] = env.get('MAYA_MODULE_PATH', '') + ':' + path
                modList = [ m for m in os.listdir( path ) if m.endswith('.mod') ]
                if not modList:
                    logger.warning( 'No extra modules found in directory' )
            else:
                logger.warning() "Maya extra modules path referenced not found:", path )

        return environment


def mayabatchExecution( pathSceneTMP, mentalRay ):
    """This is what get executed in the mayabatch process"""
    if mentalRay:
        import lib_cmds as libb
        libb.mentalRayLoader()
    pathSceneTMP = pmc.openFile ( pathSceneTMP, force=True)
    command = libb.unPickleObject( pathSceneTMP.replace( pathSceneTMP.ext, '.pickle') )
    command.executeMayabatch()







class Monitor(object):
    """UI to check all the present and past jobs launched"""
    def __init__(self):
        for i in Mayabatch.instances:
            print i
        pass
