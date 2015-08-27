import os
import logging
import functools
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import maya.cmds as cmds
import pymel.core as pmc
import lib.lib as tdLib
import lib.stats as tdStats
logger = logging.getLogger(__name__)

initstats = tdStats.Stats('OutPlaceholder', 'regnareb', '1')



def create_text_image(filepath, title, subtitle, resolution=1024, fill_color=(255, 255, 255), fontPath='/usr/share/fonts/truetype/DejaVuSans.ttf'):
    img = Image.new("RGB", (resolution, resolution), fill_color)
    draw = ImageDraw.Draw(img)

    dictionary = {title: [50, 50, (80, 80, 80)], subtitle: [70, -50, (10, 10, 10)]}
    for text, values in dictionary.iteritems():
        fontsize, offset, color = values
        font = ImageFont.truetype(fontPath, fontsize)
        width, height = draw.textsize(text, font)
        draw.text(((resolution - width) * 0.5, (resolution - height) * 0.25 - offset), text, color, font)
        draw.text(((resolution - width) * 0.5, ((resolution - height) * 0.75) - offset), text, color, font)
    img.save(filepath)
    return True

def getExportPath():
    """ Return the absolute path and the name of the asset """
    return '/final/path/'


class Placeholder():
    def __init__(self, shaders, fillColor=(255, 255, 255)):
        self.fillColor = fillColor
        self.exportPath, self.assetName = getExportPath()
        tdLib.createDir(self.exportPath)
        self.shaders = dict.fromkeys(shaders)

    def generate(self):
        for shader in self.shaders.keys():
            assignation = tdLib.getShaderAssignation(shader)
            filename = self.assetName.upper() + '_' + shader + '_Small.tga'
            fullpath = os.path.join(self.exportPath, filename)
            text = create_text_image(fullpath, self.assetName, shader, 1024, self.fillColor)
            texture, placed2dtexture = tdLib.createFileNode()
            cmds.connectAttr(texture + '.outColor', shader + '.color', force=True)
            cmds.setAttr(texture + '.fileTextureName', fullpath, type='string')
            self.shaders[shader] = [assignation, fullpath, texture, placed2dtexture]

    def create_high(self, path):
        img = Image.open(path)
        img = img.resize((4096, 4096), Image.NEAREST)
        pathHigh = path.replace('/SMALL/', '/HIGH/', 1).replace('_Small.tga', '.tga', 1)
        img.save(pathHigh)
        return pathHigh

    def reinitialise_texture(self):
        for shader, attr in self.shaders.items():
            texture = attr[2]
            placed2dtexture = attr[3]
            cmds.setAttr(placed2dtexture + '.rotateFrame', 0)
            cmds.setAttr(placed2dtexture + '.repeatU', 1)
            cmds.setAttr(placed2dtexture + '.repeatV', 1)
            cmds.setAttr(placed2dtexture + '.offsetU', 0)
            cmds.setAttr(placed2dtexture + '.offsetV', 0)
            cmds.setAttr(texture + '.fileTextureName', cmds.getAttr(texture + '.fileTextureName'), type='string')

    def extract_combine(self, assignation):
        mesh = list(set([mesh.split('.')[0] for mesh in assignation]))
        if len(mesh) > 1:
            mesh = cmds.polyUnite(mesh)
        return cmds.filterExpand(mesh, sm=12)

    def bake(self):
        for shader, attr in self.shaders.items():
            t = initstats.emit('bake', True)
            assignation = attr[0]
            path = attr[1]
            texture = attr[2]
            Umin, Vmin = tdLib.getUDIM(assignation)
            with tdLib.UndoContext():
                assignation = self.extract_combine(assignation)
                dummyFile = cmds.convertSolidTx(texture + '.outColor', assignation, fileImageName=path, antiAlias=1, backgroundMode=2, resolutionX=512, resolutionY=512, fileFormat='tga', uvRange=[Umin, Umin+1, Vmin, Vmin+1])
            cmds.undo()
            self.reinitialise_texture()
            logger.info(self.create_high(path))
            logger.info(path)
            t.stop()


class PlaceholderUI():
    def __init__(self, placeholder):
        initstats.emit('open')
        self.placeholder = placeholder
        self.shaders = placeholder.shaders

    def rotate(self, *args):
        for shader in self.shaders.values():
            cmds.setAttr(shader[3] + '.rotateFrame', args[0])

    def repeat(self, *args):
        for shader in self.shaders.values():
            cmds.setAttr(shader[3] + '.repeatU', args[0])
            cmds.setAttr(shader[3] + '.repeatV', args[0])

    def offsetU(self, *args):
        for shader in self.shaders.values():
            cmds.setAttr(shader[3] + '.offsetU', -args[0])

    def offsetV(self, *args):
        for shader in self.shaders.values():
            cmds.setAttr(shader[3] + '.offsetV', -args[0])

    def execute(self, *args):
        self.interface['mainWindow'].delete()
        self.placeholder.bake()

    def showUI(self):
        self.interface = {}
        windowTitle = 'Out Placeholder'
        if pmc.window(windowTitle.replace(" ", "_"), exists=True):
            pmc.deleteUI(windowTitle.replace(" ", "_"), window=True)

        columWidth = [[1,60], [2,60], [3,250]]
        self.interface['mainWindow'] = pmc.window(windowTitle, title=windowTitle)
        self.interface['layout'] = pmc.verticalLayout()
        self.interface['text'] = pmc.text(l=str(self.shaders.keys()), fn='boldLabelFont', h=30)
        self.interface['rotate'] = pmc.floatSliderGrp(label='Rotate UV', value=0, field=True, columnWidth=columWidth, step=0.01, minValue=-360.0, maxValue=360.0, fieldMinValue=-360.0, fieldMaxValue=360.0, dragCommand=functools.partial(self.rotate), changeCommand=functools.partial(self.rotate))
        self.interface['repeat'] = pmc.floatSliderGrp(label='Repeat UV', value=1, field=True, columnWidth=columWidth, step=0.01, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=10.0, dragCommand=functools.partial(self.repeat), changeCommand=functools.partial(self.repeat))
        self.interface['offsetV'] = pmc.floatSliderGrp(label='Offset U', value=0, field=True, columnWidth=columWidth, step=0.01, minValue=-1.0, maxValue=1.0, fieldMinValue=-1.0, fieldMaxValue=1.0, fs=0.01, dragCommand=functools.partial(self.offsetU), changeCommand=functools.partial(self.offsetU))
        self.interface['offsetV'] = pmc.floatSliderGrp(label='Offset V', value=0, field=True, columnWidth=columWidth, step=-0.01, minValue=-1.0, maxValue=1.0, fieldMinValue=-1.0, fieldMaxValue=1.0, fs=0.01, dragCommand=functools.partial(self.offsetV), changeCommand=functools.partial(self.offsetV))
        self.interface['execute'] = cmds.button(l='Get the (real) power!', c=functools.partial(self.execute))
        self.interface['layout'].redistribute()
        self.interface['mainWindow'].show()

