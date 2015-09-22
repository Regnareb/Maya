import os
import sys
import errno
import shutil

class Error(EnvironmentError):
    pass

def string2bool(string, strict=True):
    """Convert a string to its boolean value.
    The strict argument keep the string if neither True/False are found
    """
    if strict:
        return string == "True"
    else:
        if string == 'True':
            return False
        elif string == 'False':
            return True
        else:
            return string

def copytree(src, dst, symlinks=False, ignore=None):
    """Recursively copy a directory tree using copy2().

    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    createdir(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error, errors

def createdir(path):
    """Create a directory"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def copyanything(src, dst):
    try:
        copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            createdir(os.path.dirname(dst))
            shutil.copy2(src, dst)
        elif exc.errno == errno.ENOENT:
            print exc
            return False
        else:
            raise
    return True

class CreateModule(object):
    def __init__(self, name, rename=False, preview=False):
        self.name = name
        self.rename = string2bool(rename, False)
        self.preview = string2bool(preview, False)
        self.currentDir = os.getcwd()
        self.pathList = []
        self.moduleTemplate = ''

        if preview:
            print '[PREVIEW MODE]'

    def move_files(self):
        for path in self.pathList:
            self.copycontent(path)

    def copycontent(self, path):
        originalPath = os.path.join(self.currentDir, path)
        finalPath = os.path.join(self.currentDir, 'plug-ins', self.name, path)
        if not self.preview:
            copyState = copyanything(originalPath, finalPath)
        if self.preview or copyState:
            print '[Copy from/to]\n', originalPath, '\n', finalPath, '\n'
            self.delete_rename(originalPath)

    def delete_rename(self, path):
        if self.rename:
            if not self.preview:
                shutil.move(path, path + '.bak')
            print '[Rename to]\n', path, '\n', path + '.bak', '\n'
        elif os.path.isdir(path):
            if not self.preview:
                shutil.rmtree(path)
            print '[Delete]\n', path, '\n'
        else:
            if not self.preview:
                os.remove(path)
            print '[Delete]\n', path, '\n'

    def create_module_file(self):
        if not self.preview:
            createdir(os.path.join(self.currentDir, 'modules-extras'))
            with open(os.path.join(self.currentDir, 'modules-extras', self.name + '.mod'), 'w') as f:
                f.write(self.moduleTemplate)
        print '[Create module file]\n', self.moduleTemplate, '\n\n'

    def checkfiles(self):
        pluginPath = os.path.join(self.currentDir, 'plug-ins')
        modulePath = os.path.join(self.currentDir, 'modules-extras')
        excludePath = [pluginPath, modulePath]
        if self.preview:
            excludePath.extend([os.path.join(self.currentDir, i) for i in self.pathList])

        print '[Check remaining files with "%s" pattern - PLEASE WAIT]' % self.name
        for root, dirs, files in os.walk(self.currentDir, topdown=False):
            if self.name in root.lower() and not any(i in root for i in excludePath) and '.bak' not in root:
                print 'Directory still exists:', root
                continue

            for fil in files:
                path = os.path.join(root, fil)
                if self.name in fil.lower() and not any(i in path for i in excludePath) and '.bak' not in path:
                    print 'File still exists', path
                    continue
        print '[Check end]'


class TurtleModule(CreateModule):
    def __init__(self, rename=False, preview=False):
        super(TurtleModule, self).__init__('turtle', rename, preview)
        self.pathList = ['bin/plug-ins/Turtle.so', 'bin/etc/turtlebakeRenderer.xml', 'bin/etc/turtleRenderer.xml', 'bin/rendererDesc/turtlebakeRenderer.xml', 'bin/rendererDesc/turtleRenderer.xml', 'scripts/turtle', 'scripts/startup/shelf_TURTLE.mel', 'icons/turtle', 'presets/ShaderFX/Scenes/TurtleShaderFX_Manual.sfx']
        self.moduleTemplate = """+ Turtle 2014.0.0 ../plug-ins/turtle
PATH+:=bin
[r] scripts: scripts
[r] icons: icons/turtle
[r] presets: presets
[r] plug-ins: bin/plug-ins/"""

        self.move_files()
        self.create_module_file()
        self.checkfiles()




if len(sys.argv) < 2:
    sys.argv.append(False)
if len(sys.argv) < 3:
    sys.argv.append(False)

TurtleModule(sys.argv[1], sys.argv[2])






