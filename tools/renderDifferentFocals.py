import os
import logging
import pymel.core as cmds
import lib.optionsWindow
logger = logging.getLogger(__name__)

__version__ = '0.0.1'


class RenderDifferentFocals( tdOptionsWindow.td_OptionsWindow ):
    def __init__(self):
        super( RenderDifferentFocals, self ).__init__()
        self.title      = 'Render Different Focals'
        self.window     = 'td_renderDifferentFocals'
        self.actionName = 'Render and Close'


    def helpMenuCmd(self, *args):
        """Open a browser to the online doc"""
        cmds.launch(webPage="http://www.google.com")


    def editMenuResetCmd(self, *args):
        """Reset the options to the default ones"""
        self.interface['TimeRange'].setSelect(1)
        self.interface['StartTime'].setEnable(False)
        self.interface['EndTime'].setEnable(False)
        self.interface['StartTime'].setValue1(1)
        self.interface['EndTime'].setValue1(10)
        self.interface['Focals'].setText( '20, 25, 30, 35' )
        self.getCameras()
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type='string')
        cmds.setAttr('defaultRenderGlobals.imageFormat', 32 )


    def applyBtnCmd(self, *args):
        """Check for double curve then move the CVs[0] and snap it to the emitter"""
        self.timeRange  = self.interface['TimeRange'].getSelect()
        self.startTime  = self.interface['StartTime'].getValue()[0]
        self.endTime    = self.interface['EndTime'].getValue()[0]
        self.focals     = map( int, self.interface['Focals'].getText().split(',') )
        # self.interface['Cameras'].getValue()

        if self.timeRange == 1:
            self.startTime = cmds.playbackOptions( query=True, minTime=True)
            self.endTime   = cmds.playbackOptions( query=True, maxTime=True)


        for camera in self.renderCameras:
            renderKeys = sorted( list( set( cmds.keyframe( camera, time=(startTime, endTime), query=True ))))
            for key in renderKeys:
                for focal in self.focals:
                    cmds.currentTime( key, edit=True )
                    cmds.setAttr( getShapes(camera)[0] + '.focalLength', focal )
                    tempPath = cmds.Mayatomr( preview=True, cam=camera )
                    extension = os.path.splitext( tempPath )[1]
                    finalPath = '/Desktop/render/%s_key%s_focal%s%s' % ( camera.replace(':', '_'), int(key), focal, extension )
                    shutil.move( tempPath, finalPath )
                    

                    


            

    def displayOptions( self ):
        """Build the interface"""
        self.interface['TimeRange'] = cmds.radioButtonGrp( numberOfRadioButtons=2, label='Time Range', labelArray2=['Time Slider', 'Start/End'], onCommand=self.disableTimeRange )
        self.interface['StartTime'] = cmds.intFieldGrp( label='Start Time' )
        self.interface['EndTime']   = cmds.intFieldGrp( label='End Time' )
        self.interface['Focals']    = cmds.textFieldGrp( label='Focals' )
        self.interface['Cameras']   = cmds.textScrollList( allowMultiSelection=True, width=200, height=100 )
        # self.interface['CamerasLabel']   = cmds.text( label='Cameras' )

        self.formAttachPosition()

        cmds.formLayout(
            self.optionsForm, e=True,
            attachForm=(
                [ self.interface['TimeRange'], 'top', 10 ],
                [ self.interface['Cameras'], 'bottom', 100 ],
                [ self.interface['Cameras'], 'left', 150 ],
            ),
            attachControl=(
                [ self.interface['StartTime'], 'top', 0, self.interface['TimeRange'] ],
                [ self.interface['EndTime'], 'top', 0, self.interface['StartTime'] ],
                [ self.interface['Focals'], 'top', 0, self.interface['EndTime'] ],
                [ self.interface['Cameras'], 'top', 10, self.interface['Focals'] ],
                # [ self.interface['CamerasLabel'], 'top', 10, self.interface['Focals'] ],
                # [ self.interface['CamerasLabel'], 'right', -90, self.interface['Cameras'] ],
            ),
            attachNone=(
                [ self.interface['Cameras'], 'left' ],
                [ self.interface['Cameras'], 'right' ],
            )
        )
        self.editMenuResetCmd() # Set the default values in the interface


    def disableTimeRange(self, *args):
        if self.interface['TimeRange'].getSelect() == 1:
            self.interface['StartTime'].setEnable(False)
            self.interface['EndTime'].setEnable(False)
        else:
            self.interface['StartTime'].setEnable(True)
            self.interface['EndTime'].setEnable(True)


    def getCameras(self):
        allCameras      = cmds.listCameras(perspective=True)
        selection       = cmds.ls(sl=True)
        self.renderCameras    = [i for i in allCameras if i in selection]

        for camera in allCameras:
            cmds.textScrollList( self.interface['Cameras'], edit=True, append=camera )
            cmds.setAttr( getShapes(camera)[0] + '.renderable', 0)
            # cmds.menuItem( label=camera )

        for camera in self.renderCameras:
            cmds.textScrollList( self.interface['Cameras'], edit=True, selectItem=camera)
            cmds.setAttr( getShapes(camera)[0] + '.renderable', 1)
        

RenderDifferentFocals.showUI()
