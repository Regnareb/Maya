"""Use the linux notify-send command to notify the user.

notif = Notify()
notif.setTitle('Uber Title')
notif.setMessage('Message of the <b>notification</b>.')
notif.setIcon('dialog-information')
notif.setTimeout(0)
notif.send()
"""
import os
import logging
logger = logging.getLogger(__name__)


class Notify(object):
    def __init__(self, **kwargs):
        self.title = " "
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def setTitle(self, title):
        self.title = title

    def setMessage(self, message):
        self.message = message

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setUrgency(self, urgency):
        self.urgency = urgency

    def setCategory(self, category):
        self.category = category

    def setIcon(self, icon):
        self.icon = icon

    def setHint(self, hint):
        self.hint = hint

    def _constructCmd(self):
        cmd = 'notify-send'
        order = ['title', 'message', 'timeout', 'urgency', 'category', 'icon', 'hint']
        attributes = {'title': ' "{}"', 'message': ' "{}"', 'timeout': ' -t {}', 'urgency': ' -u {}', 'category': ' -c {}', 'icon': ' -i {}',  'hint': ' -h {}'}
        for attr in order:
            try:
                value = getattr(self, attr)
                cmd += attributes[attr].format(value)
            except AttributeError:
                pass
        logger.debug(cmd)
        return cmd

    def send(self):
        cmd = self._constructCmd()
        os.system(cmd)





"""notifykde(title='title', text='message')"""
import dbus

def notifykde(event='warning', fromApp='kde', contexts=[], title='', text='', pixmap=[], actions=[], timeout=0, winId=0, dbus_interface="org.kde.KNotify"):
    knotify = dbus.SessionBus().get_object("org.kde.knotify", "/Notify")
    knotify.event(event, fromApp, contexts, title, text, pixmap, actions, timeout, winId, dbus_interface=dbus_interface)
