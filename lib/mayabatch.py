"""
This class is used to do deported processing, mainly to not pollute the scene with nodes related to Mentalray, Turtle, etc..

It will launch an instance of maya in batch mode, and execute the mayabatchExecution() function with a path to the maya scene exported, and a pickle passed as the argument 'objectRecorded' (saved in the '/tmp' folder).
The nodes exported is defined by the 'exportList' argument. If set to an empty list, it will export the scene as is. If set to False, it won't export anything, and use the original scene.

The maya -batch instance is executed in a thread, this way the user can still use its main Maya during the other one is processing. You can override this behaviour by setting the 'block' argument to True.
The mayabatchExecution() function will then open the maya scene passed as argument, unpickle the object in the second argument, and execute its 'executeMayabatch' method.

If maya crashes, it will execute it again 2 times.
At the end, if it still crashed, it will send a mail to the user with all the log. Otherwise it will send a mail with the result (if the argument 'mailEnabled' is set).
The mailEnabled argument is a list of two elements, the first one is the title of the tool that goes in the subject of the mail.
The second one is the begining message you want to send. I usually recap here the elements to process.
At the end of the mail -if the process didn't failed- it will use the last 2 lines printed in the mayabatch process (look in TheBakery module to see how I used it).

The tdStats of the original script can be passed as an argument to track the stats specific to that tool.
"""


import os
import time
import uuid
import copy
import atexit
import logging
import threading
import subprocess
import maya.cmds as cmds
import tdLib
import tdStats
import tdMail
logger = logging.getLogger(__name__)

initstats = tdStats.Stats('Mayabatch', 'regnareb', '8')



class Mayabatch(threading.Thread):
    instances = []

    def __init__(self, objectRecorded='', exportList=[], modulesExtra=False, block=False, mailEnabled=False, mailOnlyCrash=False, stats=None):
        super(Mayabatch, self).__init__()
        Mayabatch.instances.append(self)
        self.__initialized  = True
        self.uuid           = uuid.uuid4().hex
        self.objectRecorded = objectRecorded
        self.exportList     = exportList
        self.modulesExtra   = modulesExtra
        self.mailEnabled    = mailEnabled
        self.mailOnlyCrash  = mailOnlyCrash
        self.formatStats(stats)
        self.totalTime      = self.tdStats.emit('total', True)
        self._stop          = threading.Event()
        self.tmp        = '/tmp/'
        atexit.register(self.stop)
        self.saveState()
        # self.setDaemon(True)
        self.start()
        if block: self.join()

    def __repr__(self):
        r = super(Mayabatch, self).__repr__()
        if self.exitcode:
            r = r.replace('stopped', 'crashed')
        return r

    def run(self):
        tries = range(3)
        tries.reverse()
        cmd = 'maya -batch -command \'callPython "lib.mayabatch" "mayabatchExecution" { "%s", "%s", "%s" }\'' % (self.pathScene, self.pathPickle, self.modulesExtra)
        for tries_remaining in tries:
            self.maya          = subprocess.Popen(cmd,
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  env=self.getEnvironment(),
                                                  shell=True)
            self.out, self.err = self.maya.communicate()
            self.exitcode      = self.maya.returncode
            logger.debug('Mayabatch out: {}'.format(self.out))
            logger.debug('Mayabatch error: {}'.format(self.err))
            logger.debug('Mayabatch exitcode: {}'.format(self.exitcode))
            if not self.exitcode:
                break
            else:
                self.tdStats.emit('crash')
        self.returnSignal()
        self.getTimers()
        if self.mailEnabled: self.sendMail()
        self.stop()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def returnSignal(self):
        if self.exitcode != 0:
            logger.debug(self.out)
            logger.error('Error in thread: %s' % (self.err))
        else:
            self.result = self.out.splitlines()[-2]
            logger.info('%s' % (self.result))

    def saveState(self):
        self.saveTime = self.tdStats.emit('save', True)
        activeViewport = tdLib.getActiveViewport()
        if self.exportList == False:
            # Do not export, use the original scene
            logger.debug('Use original scene.')
            self.pathScene = cmds.file(sceneName=True, query=True)
            self.pathPickle = tdLib.formatPath(self.uuid + '.pickle', self.tmp)
        else:
            if activeViewport and not self.exportList:
                isolateSets = cmds.isolateSelect(activeViewport, viewObjects=True, query=True)
                if isolateSets:
                    # remove mskMaterial and tmpObjFinal when baking is fixed
                    self.exportList = cmds.sets(isolateSets, query=True) + cmds.ls(type='textureBakeSet') + cmds.ls('mskMaterial*') + cmds.ls('tmpObjFinal_outPlaceHolderShape')
            logger.debug('Export {}'.format(self.exportList))
            self.pathScene = tdLib.export(self.exportList, path=self.tmp, suffix=self.uuid) # If the export list is empty, it will export everything
            self.pathPickle = tdLib.replaceExtension(self.pathScene, '.pickle')
        tdLib.pickleObject(self.pathPickle, self.objectRecorded)
        self.saveTime.stop()

    def formatStats(self, stats):
        '''Concatenate the stats infos or just use use the mayabatch one if none are specified in the main tool.'''
        if stats:
            self.tdStats = copy.deepcopy(stats)
            self.tdStats.params['tool'] = '|'.join([self.tdStats.params['tool'], initstats.params['tool']])
            self.tdStats.params['author'] = '|'.join([self.tdStats.params['author'], initstats.params['author']])
            self.tdStats.params['version'] = '|'.join([self.tdStats.params['version'], initstats.params['version']])
        else:
            self.tdStats = initstats
        self.tdStats.createSession()

    def getTimers(self):
        try:
            openTime, execTime = self.out.splitlines()[-1].split(' ')
            t = self.tdStats.emit('open', True)
            openTime = t.stop(openTime)
            t = self.tdStats.emit('exec', True)
            execTime = t.stop(execTime)
        except (IndexError, ValueError):
            openTime, execTime = None, None
        self.totalTime.stop()
        self.timers = [self.totalTime.elapsed, self.saveTime.elapsed, openTime, execTime]

    def sendMail(self):
        user        = os.environ['USER']
        destination = user + '@yourstudio.com'
        subject     = '%s batch result' % (self.mailEnabled[0])
        message     = ''
        message += '%s<br />' % (self.mailEnabled[1])
        if self.exitcode !=0:
            message += '<b style="color:red">Crashed: </b><br />' + self.err.replace('\n', '<br />') + '<br /><br /><b style="color:red">Log:</b><br /> ' + self.out.replace('\n', '<br />') + '<br />'
            subject += ': Crashed'
        else:
            message += '<b style="color:green">Success:</b><br />' + self.result.replace('\n', '<br />') + '<br /><br /><br /><br /><br />'
            for s, i in zip(['Total', 'Save', 'Open', 'Bake'], self.timers):
                message += '<span style="color:#fff">%s time: %ss</span><br />' % (s, i)
            subject += ': Success'

        if self.mailOnlyCrash and self.exitcode !=0 or not self.mailOnlyCrash:
            tdMail.sendMail('noreply@yourstudio.com', [destination], subject, message)

    def getEnvironment(self):
        environment = os.environ.copy()
        if self.modulesExtra:
            path = os.path.join(os.environ['MAYA_LOCATION'], 'modules-extras')
            if os.path.exists(path):
                environment['MAYA_MODULE_PATH'] = environment.get('MAYA_MODULE_PATH', '') + ':' + path
                modList = [ m for m in os.listdir(path) if m.endswith('.mod') ]
                if not modList:
                    logger.warning('No extra modules found in directory')
            else:
                logger.warning('Maya extra modules path referenced not found: %s', path)
        return environment


def mayabatchExecution(pathScene, pathPickle, modulesExtra):
    """This is what get executed in the mglmayabatch process"""
    modulesExtra = tdLib.string2bool(modulesExtra, strict=False)
    if isinstance(modulesExtra, basestring):
        tdLib.loadPlugin(modulesExtra)
    t = time.time()
    pathScene = cmds.file(pathScene, open=True, force=True)
    openTime = time.time() - t
    command = tdLib.unPickleObject(pathPickle)
    t = time.time()
    command.executeMayabatch()
    execTime = time.time() - t
    print openTime, execTime








class Monitor(object):
    """UI to check all the present and past jobs launched"""
    def __init__(self):
        for i in Mayabatch.instances:
            print i
        pass
