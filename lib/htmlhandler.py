import re
import logging


class HtmlStreamHandler(logging.StreamHandler):

    CRITICAL = {'color': 'red', 'size': '100%', 'special': '', 'after': '' }
    ERROR    = {'color': 'red', 'size': '100%', 'special': '', 'after': ''}
    WARNING  = {'color': 'yellow', 'size': '100%', 'special': '', 'after': ''}
    INFO     = {'color': 'aqua', 'size': '100%', 'special': '', 'after': ''}
    DEBUG    = {'color': 'aquamarine', 'size': '100%', 'special': '', 'after': ''}
    RAINBOW  = {'color': 'transparent', 'size': '100%', 'special':
                'background-image: -webkit-gradient( linear, left top, right top, color-stop(0, #f22), color-stop(0.15, #f2f), color-stop(0.3, #22f), color-stop(0.45, #2ff), color-stop(0.6, #2f2),color-stop(0.75, #2f2), color-stop(0.9, #ff2), color-stop(1, #f22));\
                background-image: gradient( linear, left top, right top, color-stop(0, #f22), color-stop(0.15, #f2f), color-stop(0.3, #22f), color-stop(0.45, #2ff), color-stop(0.6, #2f2),color-stop(0.75, #2f2), color-stop(0.9, #ff2), color-stop(1, #f22) );\
                -webkit-background-clip: text;\
                background-clip: text;\
                display: inline-block;',
                'after': ''}

    def __init__(self, stream=None):
        super(HtmlStreamHandler, self).__init__()

    @classmethod
    def _get_params(cls, level):
        if level == 777:               return cls.RAINBOW  # logger.log(777, 'Message')
        elif level >= logging.CRITICAL:return cls.CRITICAL
        elif level >= logging.ERROR:   return cls.ERROR
        elif level >= logging.WARNING: return cls.WARNING
        elif level >= logging.INFO:    return cls.INFO
        elif level >= logging.DEBUG:   return cls.DEBUG
        else:                          return cls.DEFAULT

    def format(self, record):
        regex = "((?:\w):(?:\\\|/)[^\s/$.?#].[^\s]*)"
        regex = re.compile(regex, re.MULTILINE)
        text = logging.StreamHandler.format(self, record)
        text = re.sub(regex, '<a href="file:///\g<1>">\g<1></a>', text)
        params = self._get_params(record.levelno)
        return '<span class="{1}" style="color:{color};font-size:{size};{special}">{0}</span>{after}'.format(text, record.levelname.lower(), **params)


def getlogger(logger):
    logging.basicConfig()
    root = logging.getLogger(logger)
    if isbatch():
        root.propagate = False
        ch = HtmlStreamHandler()
        formatter = logging.Formatter('%(name)s.%(funcName)s() line %(lineno)d : %(levelname)s : %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
    return root


def isbatch(default=False):
    try:
        import maya.cmds as cmds
        return cmds.about(batch=True)
    except ImportError:
        pass

    try:
        import hou
        return hou.isUIAvailable()
    except ImportError:
        pass

    return default

