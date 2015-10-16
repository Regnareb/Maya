import os
import re
import copy
import logging
import itertools
import maya.mel as mel
import maya.cmds as cmds
import lib.lib as tdLib
import lib.stats as tdStats
import lib.mayabatch as mayabatch

logger = logging.getLogger(__name__)
initstats = tdStats.Stats('TheBakery', 'regnareb', '1')


class NoAssignation(ValueError):
    pass

class Shader(object):
    instances = []
    def __init__(self, shaderName, mode, renderAttr, shaderAttr):
        self.mode = mode
        self.name = shaderName
        self.shadingGroup = tdLib.getSGsFromMaterial(shaderName)[0]
        self.renderAttr = renderAttr
        self.shaderAttr = shaderAttr
        self.assignation = tdLib.getShaderAssignation(shaderName)
        self.shapes = self.getShapes()
        self.udims = self.getAllUDIMs()
        self.udimsTotal = copy.copy(self.udims)
        self.texturePath, self.fileName = self.getTexturePath()
        # self.checkValidity()
        Shader.instances.append(self)

    def __eq__(self, other):
        return type(other) is type(self) and self.name == other.name and self.mode == other.mode

    def __repr__(self):
        return self.name

    def getShapes(self):
        shapes = cmds.ls(self.assignation, shapes=True, long=True)
        assign = list(set([i.split('.')[0] for i in self.assignation])) # CLEAN THIS MESS
        assign = list(tdLib.flatten([tdLib.getShapes(i) for i in assign])) # CLEAN THIS MESS
        shapes = shapes + assign
        if not shapes:
            raise NoAssignation('No shapes assigned to that shader')
        return shapes

    def getAllUDIMs(self):
        udim = []
        for i in self.assignation:
            if '.' not in i:
                faceList = cmds.ls(i + '.f[*]', flatten=True)
            else:
                faceList = cmds.ls(i, flatten=True)
            for face in faceList:
                udim.append(tdLib.getUDIM(face))

        udim.sort()
        udim = list(k for k,_ in itertools.groupby(udim))
        return udim

    def getTexturePath(self):
        folder, assetName = self.getExportPath(self.mode)
        filename = assetName + '_' + self.name + '_' + self.mode
        return folder, filename

    def getExportPath(self, mode):
        """ Return the absolute path and the name of the asset """
        return '/final/path/', 'filename'

    def checkValidity(self):
        for i in reversed(range(len(Shader.instances))):
            if Shader.instances[i] == self:
                del Shader.instances[i]

    def setFilename(self, text):
        self.fileName = text


class Bakery(object):
    def __init__(self):
        self.project = ''
        self.result = []
        self.toBake = []
        self.shaders = Shader.instances
        self.renderAttr = {'resolution': 2048,
                           'alpha': 0,
                           'merge': 1,
                           'tbBilinearFilter': 0,
                           'tbEdgeDilation': 0,
                           'tbUvRange': 2,
                           'tbDirectory': '/tmp/'
                           }
        self.shaderAttr = {'OCC': {'minSamples': 128,
                                   'maxSamples': 256,
                                   'coneAngle': 180.0,
                                   'maxDistance': 5,
                                   'contrast': 1.0,
                                   'scale': 1.0,
                                   'selfOcclusion': 0
                                   },
                           'THICK': {'numberOfRays': 16,
                                     'coneAngle': 80,
                                     'maxDistance': 0.75
                                     },
                           'DIRT': {'LeaksOn': 1,
                                    'LeaksGlobalScale': 1,
                                    'LeaksDistance': 40,
                                    'LeaksGamma': 1,
                                    'LeaksLacunarity': 0,
                                    'LeaksLacunarityScale': 1,
                                    'LeaksYmultiplier': 1.5,
                                    'LeaksYScaleMult': 1,
                                    'LeaksOcclusionScale': 1,
                                    'ThicknessOn': 1,
                                    'ThicknessDistance': 0.1,
                                    'OmniDirtOn': 1,
                                    'OmniDirtPatternScale': 1,
                                    'OmniDirtMaxDistance': 5,
                                    'OmniDirtGamma': 0.8,
                                    'VertexPaintDirt': 0,
                                    'VertexPaintDirtScale': 0.2,
                                    'SplitToRGB': 0,
                                    },
                           'RGB': {},
                            }
        self.toolName = 'The Bakery'
        self.prepared = False
        self.scenePath = cmds.file(query=True, sceneName=True)
        try:
            tdLib.loadPlugin('Turtle')
            self.turtle = True
        except RuntimeError:
            self.turtle = False

    def addShaders(self, mode):
        shaders = []
        selection = cmds.ls(sl=True, geometry=True, transforms=True)
        shaderList = [tdLib.getMaterialFromSG(sg) for sublist in [tdLib.getSGsFromShape(shape) for shape in selection] for sg in sublist]
        shaderList += cmds.ls(sl=True, materials=True)
        shaderList = list(set(shaderList))
        for shaderName in shaderList:
            shader = self.addShader(shaderName, mode)
            shaders.extend([shader])
        return filter(None, shaders)

    def addShader(self, shaderName, mode):
        try:
            shader = Shader(shaderName, mode, self.renderAttr.copy(), self.shaderAttr[mode].copy())
            return shader
        except NoAssignation:
            logger.error('Shader not added, no shapes assigned to the shader')
        except AttributeError:
            logger.error('The shader is not valid. Check its name')
        return None

    def removeShader(self, shader):
        self.shaders.remove(shader)

    def constructTurtleCommand(self, shader, udim, filename, forcePath=None, dividor=1):
        directory = shader.texturePath
        if forcePath:
            directory = tdLib.normpath(forcePath)
        resolution = int(shader.renderAttr['resolution'] / dividor)
        alpha = shader.renderAttr['alpha']
        merge = shader.renderAttr['merge']
        bilinear = shader.renderAttr['tbBilinearFilter']
        edgeDilation = shader.renderAttr['tbEdgeDilation']
        UvRange = shader.renderAttr['tbUvRange']
        Umin, Vmin = udim
        cmd = 'ilrTextureBakeCmd '
        for shape in shader.shapes:
            cmd = cmd + '-target "%s" ' % shape
        cmd = cmd + '-camera "persp" -directory "%s" -fileName "%s" -width %s -height %s -alpha %s -bilinearFilter %s -edgeDilation %s -merge %s -uvRange %s -uMin %s -uMax %s -vMin %s -vMax %s ' % (
                                      directory, filename, resolution, resolution, alpha, bilinear, edgeDilation, merge, UvRange, Umin, Umin + 1, Vmin, Vmin + 1)
        logger.debug(cmd)
        return cmd

    def mergeExportList(self):
        """Keep the existing scene if turtle is loaded.
        If there is an occlusion or dirt in the bake, export everything.
        If not then export only what is needed.
        """
        exportList = []
        export = self.getPreference('Export')
        for shader in self.shaders:
            if export == 'original':
                exportList = False
                break
            elif export == 'all' or any([shader.mode == 'OCC', shader.mode == 'DIRT']) and export == 'auto':
                exportList = []
                break
            elif export == 'auto' or export == 'selection':
                exportList.extend([shape.split('.')[0] for shape in shader.shapes])
        if export == 'selection':
            exportList += cmds.ls(sl=True)
        return exportList

    def mail(self):
        """The content of the message that will be sent by the engine at the end of the job."""
        shaders = [str(shader) for shader in self.shaders]
        message = '<b>Tool:</b> %s <br /> <b>Asset:</b> %s <br /><b>Shaders:</b><br /> %s <br />'  % (self.toolName, self.scenePath, '<br />'.join(shaders))
        return self.toolName, message

    def sendBatch(self):
        old = self.prepared
        self.prepared = False
        cmds.savePrefs(general=True)
        mayabatch.Mayabatch(objectRecorded=self, exportList=self.mergeExportList(), mailEnabled=self.mail(), modulesExtra=True, stats=initstats)
        self.prepared = old

    def createShaders(self):
        """Create only once the different shaders used to bake for the different modes"""
        if not self.prepared:
            # OCC
            self.occ = cmds.createNode('ilrOccSampler') # create shader
            self.occSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.occ + 'SG')
            cmds.connectAttr(self.occ + '.outColor', self.occSG + '.surfaceShader', force=True)

            # THICKNESS
            thickShader = cmds.shadingNode('surfaceShader', asShader=True)
            self.thickSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=thickShader + 'SG')
            cmds.connectAttr(thickShader + '.outColor', self.thickSG + '.surfaceShader', force=True)
            self.thick = cmds.shadingNode('ilrSurfaceThickness', asUtility=True)
            cmds.connectAttr(self.thick + '.outThickness', thickShader + '.outColor', force=True)

            # DIRT
            nodes = cmds.file('path_to_your_file_shader.ma', reference=True, returnNewNodes=True, namespace='DIRT')
            self.dirt = cmds.ls(nodes, type='surfaceShader')[0]
            self.dirtSG = tdLib.getFirstItem(cmds.listConnections(self.dirt + '.outColor', source=False))
            if not self.dirtSG:
                self.dirtSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.dirt + 'SG')
                cmds.connectAttr(self.dirt + '.outColor', self.dirtSG + '.surfaceShader', force=True)
            self.dirt = self.dirtSG

            # RGB
            self.rgb = cmds.shadingNode('surfaceShader', asShader=True)
            self.rgbSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.rgb + 'SG')
            cmds.connectAttr(self.rgb + '.outColor', self.rgbSG + '.surfaceShader', force=True)

            self.prepared = True

    def assignShader(self, shader):
        cmds.sets(shader.assignation, edit=True, forceElement=getattr(self, shader.mode.lower() + 'SG')) # assign to the shapes

    def reassignShader(self, shader):
        cmds.sets(shader.assignation, edit=True, forceElement=shader.shadingGroup) # assign to the shapes

    def setAttributes(self, shader):
        self.setPreset(self.getPreference('Preset'))
        cmds.setAttr('defaultRenderGlobals.ren', 'turtle', type='string')
        cmds.setAttr('TurtleRenderOptions.renderer', 1)
        for key, value in shader.shaderAttr.iteritems():
            cmds.setAttr(getattr(self, shader.mode.lower()) + '.' + key, value)
        cmds.setAttr('TurtleDefaultBakeLayer.tbBilinearFilter', self.renderAttr['tbBilinearFilter'])
        cmds.setAttr('TurtleDefaultBakeLayer.tbEdgeDilation', self.renderAttr['tbEdgeDilation'])
        cmds.setAttr('TurtleDefaultBakeLayer.tbDirectory', self.renderAttr['tbDirectory'], type='string')
        if shader.mode == 'THICK':
            # Isolate meshes because there is a bug with Thickness when object penetrate each others
            faces = [x for x in shader.assignation if '.' in x]
            if faces:
                cmds.select(faces)
                mel.eval("InvertSelection")
                cmds.delete() # Delete and hide, or assign surfaceshader black if 'OCC'?
            toHide = list(set(cmds.ls(geometry=True, long=True)) - set(shader.shapes))
            if toHide:
                cmds.hide(toHide)
        elif shader.mode == 'RGB':
            try:
                attr = cmds.getAttr(shader.name + '.color')
            except ValueError:
                attr = cmds.getAttr(shader.name + '.outColor')
            cmds.setAttr(self.rgb + '.outColor', *attr[0], type='double3')


    def setPreference(self, setting, value):
        """Set preferences using the setSetting method or an arbitrary one for on/off preferences.
        For on/off preferences, if the value is set to False, it means it is setting the preference for the first time (default)
        """
        try:
            attr = getattr(self, 'set{}'.format(setting))
            attr(value)
            cmds.optionVar(sv=('TheBakery' + setting, value))
        except AttributeError:
            if value == False or cmds.optionVar(query='TheBakery' + setting):
                cmds.optionVar(sv=('TheBakery' + setting, ''))
            else:
                cmds.optionVar(sv=('TheBakery' + setting, 'True'))

    def getPreference(self, setting):
        if not cmds.optionVar(exists='TheBakery' + setting):
            return None
        return cmds.optionVar(query='TheBakery' + setting)

    def setPreview(self, value):
        self.dividor = float(value)

    def setExport(self, value):
        self.export = value

    @tdLib.reSelect
    def setPreset(self, preset):
        # self._preset = preset
        try:
            cmds.select('TurtleRenderOptions')
            path = os.path.join(os.path.split(__file__)[0], 'presets', '{}.mel'.format(preset))
            path = tdLib.normpath(path)
            mel.eval('source "{}"'.format(path))
        except ValueError:
            pass

    @property
    def preset(self):
        if hasattr(self, '_preset'):
            return self._preset
        self._preset = cmds.optionVar(query='TheBakeryPreset')
        if not self._preset:
            self._preset = 'high'
        return self._preset

    def bakeShader(self, shader, cmd):
        self.createShaders()
        cmds.undoInfo(openChunk=True)
        self.assignShader(shader)
        self.setAttributes(shader)
        mel.eval(cmd)
        cmds.undoInfo(closeChunk=True)
        cmds.undo()

    def render(self, shader):
        currentCam = tdLib.getActiveCamera() or 'persp'
        currentTime = cmds.currentTime(query=True)
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        cmd = 'RenderViewWindow;ilrRenderCmd -camera "%s" -frame %s -resolution %s %s' % (currentCam, currentTime, width, height)
        self.bakeShader(shader, cmd)

    @tdLib.reSelect
    def preview(self, shaders):
        for shader in shaders[::-1]:
            try:
                for udim in shader.udims:
                    filename = '{}.10{}{}.tga'.format(shader.fileName, udim[1], udim[0]+1)
                    cmd = self.constructTurtleCommand(shader, udim, filename, '/tmp', self.dividor)
                    logger.debug(cmd)
                    self.bakeShader(shader, cmd)
                pattern = '-directory \"(.*?)\" -fileName \"(.*?)\"'
                reg = re.search(pattern, cmd)
                path = tdLib.normpath(os.path.join(reg.group(1), reg.group(2)))
                nodeFile, placement = tdLib.createFileNode()
                cmds.setAttr('{}.fileTextureName'.format(nodeFile), path, type="string")
                cmds.setAttr('{}.uvTilingMode'.format(nodeFile), 3)
                cmds.setAttr('{}.uvTileProxyGenerate'.format(nodeFile), 1)
                cmds.connectAttr(nodeFile + '.outColor', shader.name + '.color', force=True)
            except ZeroDivisionError:
                self.render(shader)
            except UnboundLocalError:
                logger.warning('No UDIMs in the shader.')
            except RuntimeError as e:
                if 'cannot be connected to' in repr(e):
                    cmds.connectAttr(nodeFile + '.output3D', shader.name + '.outColor', force=True)
                if 'The destination attribute' in repr(e):
                    cmds.connectAttr(nodeFile + '.outColor', shader.name + '.outColor', force=True)
                elif 'No object matches name: {}.uvTilingMode'.format(nodeFile) in repr(e):
                    # This is used for Maya version < 2015. You could use a plusMinusAverage node instead and several file nodes to have the same effect.
                    # This old method does not displays the textures in the UV editor, but it works great in the viewport 1 unlike the current method.
                    # See revision 3897 to activate this old mode by uncommenting the code
                    pass
                else:
                    raise e

    def executeMayabatch(self):
        """The final method used to bake the textures on the deported machine.
        It will only bake the shaders in self.toBake if there is any (if a shader is selected in the UI for example),
        otherwise it will bake all the shaders added.
        """
        tdLib.loadPlugin('Turtle')
        for shader in self.toBake or self.shaders:
            print 'SHADER NAME: ', shader
            print 'SHADER MODE: ', shader.mode
            print 'Render Attr: ', shader.renderAttr
            print 'Shader Attr: ', shader.shaderAttr
        # Assign surfaceshader noir sur tous les meshes ?

        for shader in self.toBake or self.shaders:
            for udim in shader.udims:
                filename = '{}.10{}{}.tga'.format(shader.fileName, udim[1], udim[0]+1)
                cmd = self.constructTurtleCommand(shader, udim, filename)
                tdLib.createDir(shader.texturePath) # Create directory?
                self.bakeShader(shader, cmd)
                fullpath = tdLib.normpath(os.path.join(shader.texturePath, filename))
                self.result.append('<a href="file://{0}" {1}>{0}</a> - <a href="rvlink://{0}" {1}>Open in RV</a>'.format(fullpath, 'style="text-decoration: none"'))

        print '<br />'.join(self.result) # This is used by the Mayabatch lib to send the result by mail.


