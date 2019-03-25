import re
import os
import sys
import json
import time
import errno
import pickle
import inspect
import smtplib
import logging
import itertools
import functools
import subprocess
from collections import Iterable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
logger = logging.getLogger(__name__)


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def pickleObject(fullPath, toPickle):
    """ Pickle an object at the designated path """
    with open(fullPath, 'w') as f:
        pickle.dump(toPickle, f)
    f.close()


def unPickleObject(fullPath):
    """ unPickle an object from the designated file path """
    with open(fullPath, 'r') as f:
        fromPickle = pickle.load(f)
    f.close()
    return fromPickle


def jsonWrite(data, filePath, default=None):
    with open(filePath, 'w') as outfile:
        json.dump(data, outfile, default=default)


def jsonLoad(filePath):
    with open(filePath, 'r') as dataFile:
        return json.load(dataFile)


def setToList_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def getFirstItem(iterable, default=None):
    """Return the first item if any"""
    if iterable:
        for item in iterable:
            return item
    return default


def flatten(coll):
    """Flatten a list while keeping strings"""
    for i in coll:
        if isinstance(i, Iterable) and not isinstance(i, basestring):
            for subc in flatten(i):
                yield subc
        else:
            yield i


def string2bool(string, strict=True):
    """Convert a string to its boolean value.
    The strict argument keep the string if neither True/False are found
    """
    if not isinstance(string, basestring):
        return string
    if strict:
        return string.capitalize() == 'True'
    else:
        if string.capitalize() == 'True':
            return False
        elif string.capitalize() == 'False':
            return True
        else:
            return string


def createDir(path):
    """Creates a directory"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def formatPath(fileName, path='', prefix='', suffix=''):
    """ Create a complete path with a filename, a path and prefixes/suffixes
    /path/prefix_filename_suffix.ext"""
    path = os.path.join(path, "") # Delete ?
    if suffix:
        suffix = '_' + suffix
    if prefix:
        prefix = prefix + '_'
    fileName, fileExt = os.path.splitext(fileName)
    filePath = os.path.join(path, prefix + fileName + suffix + fileExt)
    return filePath


def normpath(path):
    """Fix some problems with Maya evals or some file commands needing double escaped anti-slash '\\\\' in the path in Windows"""
    return os.path.normpath(path).replace('\\', '/')


def pathjoin(*args):
    path = os.path.join(*args)
    return normpath(path)


def camelCaseSeparator(label, separator=' '):
    """Convert a CamelCase to words separated by separator"""
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r'%s\1' % separator, label)


def toNumber(s):
    """Convert a string to an int or a float depending of their types"""
    try:
        return int(s)
    except ValueError:
        return float(s)


def shorten_string(string, maxlimit, separator='.. '):
    if len(string) <= maxlimit:
        return string
    elif len(string) <= len(separator) + 2:
        return string[:maxlimit - 2] + '..'
    else:
        beginning = int(math.ceil(maxlimit / 2.))
        end = (maxlimit - beginning) * - 1
        return (string[:beginning] + separator + string[end:]) if len(string) > maxlimit else string


def incrementString(s):
    return re.sub('(\d*)$', lambda x: str(int(x.group(0)) + 1), s)


def replaceExtension(path, ext):
    if ext and not ext.startswith('.'):
        ext = ''.join(['.', ext])
    return path.replace(os.path.splitext(path)[1], ext)


def humansize(nbytes):
    suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def lstripAll(toStrip, stripper):
    if toStrip.startswith(stripper):
        return toStrip[len(stripper):]
    return toStrip


def rstripAll(toStrip, stripper):
    if toStrip.endswith(stripper):
        return toStrip[:-len(stripper)]
    return toStrip


def openfolder(path):
    if sys.platform.startswith('darwin'):
        return subprocess.Popen(['open', '--', path])
    elif sys.platform.startswith('linux'):
        return subprocess.Popen(['xdg-open', '--', path])
    elif sys.platform.startswith('win32'):
        path = path.replace('/', '\\')
        return subprocess.Popen(['explorer', path])


def openfile(path):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', path))
    elif os.name == 'nt':
        os.startfile(path)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', path))


def sendMail(sender, receivers, subject, text='', html=''):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)
    text = MIMEText(text, 'plain')
    html = MIMEText(html, 'html')
    msg.attach(text)
    msg.attach(html)
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(sender, receivers, msg.as_string())
        s.quit()
        return True
    except smtplib.SMTPException:
        logger.error('Error: unable to send email')
        return False









def withmany(method):
    """A decorator that iterate through all the elements and eval each one if a list is in input"""
    @functools.wraps(method)
    def many(many_foos):
        for foo in many_foos:
            yield method(foo)
    method.many = many
    return method


def memoizeSingle(f):
    """Memoization decorator for a function taking a single argument"""
    class memodict(dict):

        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__


def memoizeSeveral(f):
    """Memoization decorator for functions taking one or more arguments"""
    class memodict(dict):

        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)


def elapsedTime(f):
    @functools.wraps(f)
    def elapsed(*args, **kwargs):
        start = time.time()
        result =  f(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(elapsed)
        return result
    return elapsed


def restoreEnvironment(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        old = os.environ.copy()
        result =  f(*args, **kwargs)
        os.environ.update(old)
        return result
    return func


def decorateall(decorator):
    #Decorate all methods of the class with the decorator passed as argument (Python 3)
    def decorate(cls):
        for name, fn in inspect.getmembers(cls, inspect.isroutine):
            if name != '__new__':
                setattr(cls, name, decorator(fn))
        return cls
    return decorate
