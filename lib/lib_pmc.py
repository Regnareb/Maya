import re
import pickle
import pymel.core as pmc
import pprint, inspect, traceback



def getNewNodesCreated(_function):
    """ Return the new nodes created after the execution of a function """
    before = pmc.ls()
    eval(_function)
    after = pmc.ls()
    return list(set(after) - set(before))


def pickleObject(fullPath, toPickle):
    """ Pickle an object at the designated path """
    with open( fullPath, 'w' ) as f:
        pickle.dump( toPickle, f )
    f.close()


def unPickleObject(fullPath):
    """ unPickle an object from the designated file path """
    with open( fullPath, 'r' ) as f:
        fromPickle = pickle.load( f )
    f.close()
    return fromPickle


def getTypeNode(type, nodeList):
    """ Return all the nodes of a specific type from a list of node """
    filter = pmc.itemFilter( byType=type )
    return pmc.lsThroughFilter(filter, item=nodeList)


def stripShaderName(name):
    """ Return only the name of the shader """
    return re.search( "_(.*?)_", name ).group(0).strip('_')


def saveAsCopy(prefix='', suffix='', path='/tmp/'):
    """ Save the scene elsewhere while continuing to work on the original path """
    if suffix: suffix = '_' + suffix
    if prefix: prefix = prefix + '_'
    currentName = pmc.sceneName()
    fileName = currentName.basename()
    tmpPath = path + prefix + fileName.replace('.ma', suffix + '.ma')
    pmc.renameFile( tmpPath )
    pmc.saveFile()
    pmc.renameFile( currentName )
    return tmpPath


def getNumberCVs(curve):
    """Return the number of CVs of a curve"""
    numSpans = pmc.getAttr ( curve + ".spans" )
    degree   = pmc.getAttr ( curve + ".degree" )
    form     = pmc.getAttr ( curve + ".form" )
    numCVs   = numSpans + degree
    if ( form == 2 ):
        numCVs -= degree
    return numCVs


def randomXform( _operation, _list, _interval, _directions='XYZ' ):
    """Move/Rotate/Scale in random direction in XYZ"""
    g = lambda: random.uniform( _interval[0], _interval[1] )
    for item in _list:
        value = dict.fromkeys( ['X', 'Y', 'Z'], 0 )
        for i in _directions:
            value[i] = g()
        stringCmd = 'pmc.%s("%s", %s, %s, %s, relative=True)' % (_operation, item, value['X'], value['X'], value['X'])
        eval( stringCmd )


def getFirstSelection(filter=''):
    """Get the first item in the selection"""
    selection = pmc.ls(selection=True)
    if filter and selection:
        selection = pmc.filterExpand( selection, sm=filter)
    if selection:
        return selection[0]
    else:
        return ''
