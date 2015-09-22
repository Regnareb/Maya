"""
Create 4 lights and import a shader, to create some dirt on surfaces and bake it to a tga in the right folder.
It uses the mayabatch to bake it outside of the main maya.
"""

import os
import time
import shutil
import logging
import maya.mel as mel
import pymel.core as pmc
import lib.stats as tdStats
import lib.lib as tdLib
import lib.mayabatch as mayabatch
logger = logging.getLogger(__name__)

initstats = tdStats.Stats('OutDirtmap', 'regnareb', '1')


class td_outDirt(object):
    def __init__(self):
        self.lightGrp                = ''
        self.resolutionMap             = 256
        self.pathTMP                   = '/tmp/'
        self.pathFinal                 = ''
        self.assetName                 = ''
        self.textureBakeSet            = ''
        self.referencedShaderFile      = ''
        self.executedOnce              = False
        self.result                    = []
        self.scenePath                 = pmc.sceneName()           # For Batch
        self.pathFinal, self.assetName = self.getExportPath()
        self.shaderPathMR              = 'path_to_mentalray_shader.ma'
        self.shaderPath                = 'path_to_simple_shader.ma' #Obsolete


    def __mail__(self):
        assetName = os.path.join(*self.families) + os.sep + '<b>' + self.assetName + '</b>'
        message = '<b>Tool:</b> OutDirtMap <br /> <b>Asset:</b> %s <br /><b>Shaders:</b> %s <br />'  % (assetName, self.shaderList)
        return "OutDirtMap", message


    def getExportPath(self):
        """ Return the absolute path and the name of the asset """
        return '/final/path/'


    def firstExec(self, *args):
        self.saveShaderAssignation()
        self.isReferenceShaderLoaded()
        self.getShadersNodes()
        self.createLights()
        if any( self.shadersAssignation.values() ):
            self.assignShader()
            self.createBakeSet()
        self.shaderList = self.shadersAssignation.keys()
        self.executedOnce = True



    def saveShaderAssignation(self):
        """ Save shaders/objects assignation in a dictionary """
        shadersInitial = pmc.ls(sl=True, materials=True)
        if not shadersInitial:
            pmc.error('No shader(s) selected.')
        shadersInitial = [ str(i) for i in shadersInitial ]
        self.shadersAssignation = dict.fromkeys( shadersInitial, None )
        for shader in shadersInitial:
            pmc.hyperShade( objects=shader )
            self.shadersAssignation[shader] = pmc.ls(sl=True)


    def isReferenceShaderLoaded(self):
        """ Check if the shader is already referenced and reference it if not """
        if not os.path.isfile( self.shaderPath ):
            # self.shaderPath = 'path_to_mentalray_shader.ma'

        if not self.referencedShaderFile:
            referencesList = pmc.system.listReferences()
            lastIteration  = len(referencesList) - 1
            if not referencesList:
                self.referencedShaderFile = pmc.system.createReference( self.shaderPath, namespace='DH' )
            else:
                for index, currentRef in enumerate(referencesList):
                    if self.shaderPath in pmc.referenceQuery( currentRef, filename=True ):
                        self.referencedShaderFile = currentRef
                        break
                    if index == lastIteration:
                        self.referencedShaderFile = pmc.system.createReference( self.shaderPath, namespace='DH' )

        if not self.referencedShaderFile.isLoaded():
            self.referencedShaderFile.load()


    def getShadersNodes(self):
        """ Get all the shaders nodes in the reference """
        nodesInRef = pmc.system.referenceQuery( self.referencedShaderFile, nodes=True )
        self.surfaceShader = tdLib.getTypeNode('surfaceShader', nodesInRef)[0]
        self.shadingEngine = tdLib.getTypeNode('shadingEngine', nodesInRef)[0]


    def createLights(self):
        """ Create the 4 lights """
        pmc.setAttr('defaultRenderGlobals.enableDefaultLight', 0)
        if pmc.objExists('lights_grp'):
           pmc.delete('lights_grp')
        light = []
        light.append( pmc.directionalLight(name='DHdirectLight01', rotation=[-70, 0, 0]))
        light.append( pmc.directionalLight(name='DHdirectLight02', rotation=(-110, 0, 0)))
        light.append( pmc.directionalLight(name='DHdirectLight03', rotation=(-90, -20, 0)))
        light.append( pmc.directionalLight(name='DHdirectLight04', rotation=(-90, 20, 0)))
        self.lightGrp = pmc.group(light, n='lights_grp')


    def assignShader(self):
        """ Assign DH shader to objects """
        try:
            pmc.select( [x for x in self.shadersAssignation.values() if x] )
        except TypeError:
            logger.error('No object assigned to the shader!')
        else:
            pmc.hyperShade( assign=self.surfaceShader )
            pmc.button(self.interface['bake'], edit=True, noBackground=False)


    def selectShadingGroup(self, *args):
        """ Select ShaderGroup and open the Attribute Editor"""
        pmc.select( self.shadingEngine, noExpand=True )
        pmc.runtime.AttributeEditor()


    def createBakeSet(self):
        """Create the texture bake set"""
        if not self.textureBakeSet:
            newNodes = tdLib.getNewNodesCreated( "pmc.mel.createAndAssignBakeSet('textureBakeSet', '')" )
            self.textureBakeSet = tdLib.getTypeNode( 'textureBakeSet', newNodes )[0]
            self.textureBakeSet.setAttr( 'xResolution', self.resolutionMap )
            self.textureBakeSet.setAttr( 'yResolution', self.resolutionMap )
            self.textureBakeSet.setAttr( 'fileFormat', 6 )
            self.textureBakeSet.setAttr( 'bakeToOneMap', 1 )


    def bake(self):
        """Bake the images to the disk and move them in the correct path"""
        self.result = []
        if not self.shaderList:
            self.shaderList = self.shadersAssignation.keys()

        self.isReferenceShaderLoaded()

        for shader in self.shaderList:
            if not self.shadersAssignation[shader]:
                continue
            fileName = tdLib.stripShaderName(str(shader)) + '_Dirt'
            self.textureBakeSet.setAttr( 'prefix', fileName )
            self.textureBakeSet.setAttr( 'xResolution', self.resolutionMap )
            self.textureBakeSet.setAttr( 'yResolution', self.resolutionMap )
            pmc.select( self.shadersAssignation[shader] )
            pmc.convertLightmapSetup( camera='persp', bakeSetOverride=self.textureBakeSet, sh=True, keepOrgSG=True, showcpv=True, ksg=True, project=self.pathTMP)
            self.moveImgFile( fileName )
        os.chmod(self.pathTMP + 'lightMap', 0777)


    def assignOriginalShader(self, shaderList):
        """ Assignation of the initial shader"""
        for shader in shaderList:
            if self.shadersAssignation[shader]:
                pmc.select( self.shadersAssignation[shader] )
                pmc.hyperShade( assign=shader )


    # def exportList(self):
    #     exportList = None
    #     activeViewport = tdLib.getActiveViewport()
    #     if activeViewport:
    #         isolateSets = cmds.isolateSelect(activeViewport, viewObjects=True, query=True)
    #         if isolateSets:
    #             exportList = cmds.sets(isolateSets, query=True) + cmds.ls(type='textureBakeSet') +
    #     return exportList

    def moveImgFile(self, shader):
        """ Move the files from the tmp folder to the official folder """
        fileNameTMP                     = shader + '.tga'
        fileNameFinal                   = self.assetName + '_' + fileNameTMP
        fullPathTMP                     = self.pathTMP + 'lightMap/' + fileNameTMP
        fullPathFinal                   = self.pathFinal + fileNameFinal
        if os.path.isfile( fullPathTMP ):
            if not os.path.exists( self.pathFinal ):
                os.makedirs( self.pathFinal )
            shutil.copyfile( fullPathTMP, fullPathFinal )
            logger.debug( "File moved at" + fullPathFinal )
            self.result.append( fullPathFinal )
        else:
            logger.error( 'No file at ' + fullPathTMP + '. Move aborted.' )


    def clean(self, *args):
        if self.executedOnce:
            if pmc.objExists( self.textureBakeSet ): pmc.delete( self.textureBakeSet )
            self.assignOriginalShader( self.shadersAssignation.keys() )
        if pmc.objExists( self.lightGrp ): pmc.delete( self.lightGrp )
        if self.referencedShaderFile:
            self.referencedShaderFile.remove()
            self.referencedShaderFile   = ''


    def sendBatch(self, shaderList):
        if shaderList:
            self.shaderList = shaderList
        elif not hasattr(self, 'shadersAssignation'):
            pmc.error('No DirtyHenry shader assigned to any materials.')
        else:
            self.shaderList = self.shadersAssignation.keys()
        logger.info( 'Materials sent to bake: %s' % self.shaderList )
        self.getResolutionMapValue()
        thread = mayabatch.Mayabatch(objectRecorded=self, mailEnabled=self.__mail__(), modulesExtra='Mayatomr', stats=initstats)
        self.gradient()



    ''' BATCH MODE'''
    def executeMayabatch(self):
        # self.shaderPath = self.shaderPathMR
        # self.referencedShaderFile.replaceWith( self.shaderPath )
        self.bake()
        print '<br />'.join(self.result)






class td_outDirt_UI(td_outDirt):
    def __init__(self):
        super(td_outDirt_UI, self).__init__()
        self.interface      = {} # Initialise the interface dictionary
        self.windowTitle    = 'Out Dirt Map'
        self.showUI()


    def showUI(self):
        if pmc.window(self.windowTitle.replace(" ", "_"), exists=True):
            pmc.deleteUI( self.windowTitle.replace(" ", "_"), window=True )

        self.interface['mainWindow']    = pmc.window( self.windowTitle, title=self.windowTitle )
        self.interface['layout']        = pmc.verticalLayout()
        self.interface['warningText']   = pmc.text( label="Warning: Do not save the scene!\n Select some shaders then click 'Assign shader'", backgroundColor=(0.8, 0, 0) )
        self.interface['assignShader']  = pmc.button( label="Assign Shader", command=self.firstExec )
        self.interface['selectSG']      = pmc.button( label="Tweak Shader", command=self.selectShadingGroup )
        self.interface['resolutionMap'] = pmc.intField( value=self.resolutionMap, changeCommand=self.getResolutionMapValue )
        self.interface['bake']          = pmc.button( label="Bake All", command=pmc.Callback( self.sendBatch, [] ))
        self.interface['layout'].redistribute()
        self.interface['mainWindow'].show()
        # Clean if the UI is closed
        pmc.scriptJob( runOnce=True, uiDeleted=[ self.interface['mainWindow'].name(), pmc.Callback( self.clean ) ] )
        # Reset everything if the scene change
        pmc.scriptJob( runOnce=True, event=[ 'SceneOpened', pmc.Callback( self.__init__ ) ] )



    def getResolutionMapValue(self, *args):
        """Get the value of the Resolution Map entered in the field"""
        self.resolutionMap = self.interface['resolutionMap'].getValue()



    def gradient(self):
        for i in xrange(385,0,-40):
            pmc.button(self.interface['bake'], edit=True, backgroundColor=(i/1000., 0.385, i/1000.))
            pmc.refresh()
            time.sleep(0.001)
