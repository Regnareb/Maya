# Particle Mover

import maya.cmds as cmds
particleList    = cmds.filterExpand( sm=47 )
particleEmitter = particleList.split('.')[0]
particleShape   = cmds.listRelatives( particleEmitter, shapes=True )[0]

particleIds = cmds.getParticleAttr( particleList, attribute='id', array=True )
particlePos = cmds.getParticleAttr( particleList, attribute='worldPosition', array=True )
locatorPos  = cmds.getParticleAttr( particleList, attribute='worldPosition' )

locator = cmds.spaceLocator( position=(locatorPos[0], locatorPos[1], locatorPos[2]) )[0]




def moveParticles():






$gPos = $positions;
$gIds = $ids;

string $window = `window -menuBar true -title "Move Particles"`;
columnLayout -adjustableColumn true;
button -label "Apply" -command moveParticles;
button -label "Reset" -command ("setToZero(\""+$loc[0]+"\")");
button -label "Finish" -command ("delete "+$loc[0]+"; deleteUI -window "+$window+"; select -r "+stringArrayToString($particles," "));
showWindow $window;

proc moveParticles(){
    global string $gPart;
    global string $gLoc;
    global float $gPos[];
    global float $gIds[];

    string $locator = $gLoc;
    string $part = $gPart;
    float $pids[] = $gIds;
    float $posis[] = $gPos;

    string $sel[] = `ls -sl`;
    float $m[] = `xform -query -matrix $locator`;
    for($i = 0;$i<size($pids);$i++){
        float $po[] = {$posis[$i*3],$posis[$i*3+1],$posis[$i*3+2]};
        $po =  pointMatrixMult($po,$m);
        $po = {$po[0]+$m[12],$po[1]+$m[13],$po[2]+$m[14]};
        select -r ($part+".pt["+$pids[$i]+"]");
        setParticleAttr -vv $po[0] $po[1]$po[2] -at position;
    }
    select -r $gPart;
    catchQuiet(performSetNClothStartState(1));
    catchQuiet(saveInitialState($gPart));
    select -r $sel;
}
proc setToZero(string $obj){
    setAttr ($obj+".translateX") 0;
    setAttr ($obj+".translateY") 0;
    setAttr ($obj+".translateZ") 0;
    setAttr ($obj+".rotateX") 0;
    setAttr ($obj+".rotateY") 0;
    setAttr ($obj+".rotateZ") 0;
    setAttr ($obj+".scaleX") 1;
    setAttr ($obj+".scaleY") 1;
    setAttr ($obj+".scaleZ") 1;
    moveParticles();
}







