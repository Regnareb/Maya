def toggle_button():
    toggle_btn = ''
    top_shelf = mel.eval("$dummy = $gShelfTopLevel")
    current_tab = cmds.tabLayout(top_shelf, query=True, selectTab=True)
    shelf_buttons = cmds.shelfLayout(current_tab, query=True, childArray=True)
    for button in shelf_buttons:
        cmd = cmds.shelfButton(button, query=True, command=True)
        if "toggle_button()" in cmd:
            toggle_btn = button
            break
    
    status = cmds.pluginInfo('Substance', query=True, loaded=True)
    if status and toggle_btn:
        cmds.unloadPlugin('Substance')
        cmds.shelfButton(toggle_btn, edit=True, backgroundColor=(1, 0, 0))
    elif toggle_btn:  
        cmds.loadPlugin ('Substance')
        cmds.shelfButton(toggle_btn, edit=True, backgroundColor=(0, 1, 0))
toggle_button()


"""
proc toggleButton() {
global string $gShelfTopLevel;
    string $button;
    $currentTab = `tabLayout -q -st $gShelfTopLevel`;
    $shelfButtons = `shelfLayout -q -ca $currentTab`;
    for ($button in $shelfButtons)
    {
        $cmd = `shelfButton -q -c $button`;
        if ($cmd == "toggleButton()")
        break;
    }

    int $status = `pluginInfo -q -loaded DynamicaPlugin.mll`;
    if ($status == 0) {
        shelfButton -e -bgc 0 1 0 $button;
    }
    else {
        shelfButton -e -bgc 0 0 0 $button;
    }
}
toggleButton()
"""
