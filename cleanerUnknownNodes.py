"""Load official plugins and then delete unknown nodes"""

import os, sys
import maya.cmds as cmds

# global listPlugins
# listPlugins = ['dualMode','Mayatomr']

__version__ = '0.1.0'


class CleanerUnknownNodes():

    def __init__(self):
        self.listPluginsMaya = []
        self.unknownNodes    = cmds.ls( type=['unknown', 'unknownDag', 'unknownTransform'])

        self.get_official_plugins_list()
        self.get_current_plugins_list()
        self.compare_plugins()
        self.load_plugins()
        self.delete_nodes()


    def get_official_plugins_list(self):
        global listPlugins
        try:
            self.listPlugins = listPlugins
        except NameError:
            sys.exit()


    def get_current_plugins_list(self):
        pluginPaths     = os.environ['MAYA_PLUG_IN_PATH'].split(':')
        for path in pluginPaths:
            try:
                self.listPluginsMaya += os.listdir( path )
            except OSError:
                continue
        self.listPluginsMaya = [ os.path.splitext(i)[0] for i in self.listPluginsMaya ]


    def compare_plugins(self):
        compared = list( set( self.listPlugins ).intersection( self.listPluginsMaya ))
        if len( self.listPlugins ) != len( compared ):
            missingPlugs = list( set(self.listPlugins) - set(compared) )
            cmds.error("Missing plugins: ", missingPlugs )


    def load_plugins(self):
        for plugin in self.listPlugins:
            cmds.loadPlugin( plugin )
            

    def delete_nodes(self):
        for node in self.unknownNodes:
            if cmds.objExists( node ) and not cmds.reference( node, query=True, isNodeReferenced=True ):
                cmds.lockNode( node, lock=False )
                cmds.delete( node )

# CleanerUnknownNodes()
