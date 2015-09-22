"""
Create a button that flashes green when you click it, before going back to its normal color
Very hacky, just for fun
"""

import time
import pymel.core as pmc

def gradient(*args):
    for i in xrange( 0, 385, 40 ):
        pmc.button(interface['button'], edit=True, backgroundColor=(i/1000., 0.385, i/1000.))
        pmc.refresh()
        time.sleep(0.03)
    pmc.button(interface['button'], edit=True, noBackground=False)


windowName = 'Gradient'
if pmc.window(windowName, exists=True):
    pmc.deleteUI(windowName, window=True)

interface = {}
interface['mainWindow'] = pmc.window(windowName, title='test')
interface['layout'] = pmc.verticalLayout()
interface['button'] = pmc.button(label="Gradient me!", command=gradient)
interface['layout'].redistribute()
interface['mainWindow'].show()
