####################################################################################
##
# Created: Jeremy YeoKhoo, http://www.jeremyyeokhoo.com
# Modified: 15/01/2013
# Description: Checks if an object's transform is within a cameras frustum in Maya.
# Based on Dane K Barneys C++ plugin, works as a python command. The
# objectsInCameraView() is an example command that checks for all transforms and
# returns a printed statement. This command needs at least one camera selected.
##
# Disclaimer: Based on Dane K Barney's tool. http://www.danekbarney.com Can be
# modified and/or for non-commercial purposes.
##
####################################################################################

import maya.OpenMaya as OpenMaya


class plane():

    def __init__(self, normalisedVector):
        # OpenMaya.MVector.__init__()
        self.vector = normalisedVector
        self.distance = 0.0

    def relativeToPlane(self, point):
        # Converting the point as a vector from the origin to its position
        pointVec = OpenMaya.MVector(point.x, point.y, point.z)
        val = (self.vector * pointVec) + self.distance
        if (val >= 0.0):
            return True  # In front or on origin
        elif (val < 0.0):
            return False  # Behind


class frustum():

    def __init__(self, cameraName):
        # Initialising selected transforms into its associated dagPaths
        selectionList = OpenMaya.MSelectionList()
        objDagPath = OpenMaya.MDagPath()
        selectionList.add(cameraName)
        selectionList.getDagPath(0, objDagPath)
        self.camera = OpenMaya.MFnCamera(objDagPath)

        self.nearClip = self.camera.nearClippingPlane()
        self.farClip = self.camera.farClippingPlane()
        self.aspectRatio = self.camera.aspectRatio()

        left_util = OpenMaya.MScriptUtil()
        left_util.createFromDouble(0.0)
        ptr0 = left_util.asDoublePtr()

        right_util = OpenMaya.MScriptUtil()
        right_util.createFromDouble(0.0)
        ptr1 = right_util.asDoublePtr()

        bot_util = OpenMaya.MScriptUtil()
        bot_util.createFromDouble(0.0)
        ptr2 = bot_util.asDoublePtr()

        top_util = OpenMaya.MScriptUtil()
        top_util.createFromDouble(0.0)
        ptr3 = top_util.asDoublePtr()

        stat = self.camera.getViewingFrustum(self.aspectRatio, ptr0, ptr1, ptr2, ptr3, False, True)

        planes = []

        left = left_util.getDoubleArrayItem(ptr0, 0)
        right = right_util.getDoubleArrayItem(ptr1, 0)
        bottom = bot_util.getDoubleArrayItem(ptr2, 0)
        top = top_util.getDoubleArrayItem(ptr3, 0)

        # planeA = right plane
        a = OpenMaya.MVector(right, top, -self.nearClip)
        b = OpenMaya.MVector(right, bottom, -self.nearClip)
        c = (a ^ b).normal()  # normal of plane = cross product of vectors a and b
        planeA = plane(c)
        planes.append(planeA)

        # planeB = left plane
        a = OpenMaya.MVector(left, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, top, -self.nearClip)
        c = (a ^ b).normal()
        planeB = plane(c)
        planes.append(planeB)

        # planeC = bottom plane
        a = OpenMaya.MVector(right, bottom, -self.nearClip)
        b = OpenMaya.MVector(left, bottom, -self.nearClip)
        c = (a ^ b).normal()
        planeC = plane(c)
        planes.append(planeC)

        # planeD = top plane
        a = OpenMaya.MVector(left, top, -self.nearClip)
        b = OpenMaya.MVector(right, top, -self.nearClip)
        c = (a ^ b).normal()
        planeD = plane(c)
        planes.append(planeD)

        # planeE = far plane
        c = OpenMaya.MVector(0, 0, 1)
        planeE = plane(c)
        planeE.distance = self.farClip
        planes.append(planeE)

        # planeF = near plane
        c = OpenMaya.MVector(0, 0, -1)
        planeF = plane(c)
        planeF.distance = self.nearClip
        planes.append(planeF)

        self.planes = planes
        self.numPlanes = 6

    def relativeToFrustum(self, pointsArray):
        numInside = 0
        numPoints = len(pointsArray)

        for j in xrange(self.numPlanes):
            numBehindThisPlane = 0
            for i in xrange(numPoints):
                if not self.planes[j].relativeToPlane(pointsArray[i]):
                    numBehindThisPlane += 1
                if numBehindThisPlane == numPoints:
                    # all points were behind the same plane
                    return False  # Outside
                elif (numBehindThisPlane == 0):
                    numInside += 1
        if (numInside == self.numPlanes):
            return True  # Inside
        return True  # Intersect


class dkbObjectsInCameraView():

    def __init__(self, cameraName, node):
        selectionList = OpenMaya.MSelectionList()
        camDagPath = OpenMaya.MDagPath()
        selectionList.add(cameraName)
        selectionList.getDagPath(0, camDagPath)
        self.cameraName = cameraName
        self.cameraDagPath = OpenMaya.MFnCamera(camDagPath)
        self.camInvWorldMtx = camDagPath.inclusiveMatrixInverse()
        self.node = node

    def processNode(self):
        fnCam = frustum(self.cameraName)
        points = []

        # for node in self.objectList:
        selectionList = OpenMaya.MSelectionList()
        objDagPath = OpenMaya.MDagPath()
        selectionList.add(self.node)
        selectionList.getDagPath(0, objDagPath)

        fnDag = OpenMaya.MFnDagNode(objDagPath)
        obj = objDagPath.node()

        dWorldMtx = objDagPath.exclusiveMatrix()
        bbox = fnDag.boundingBox()

        minx = bbox.min().x
        miny = bbox.min().y
        minz = bbox.min().z
        maxx = bbox.max().x
        maxy = bbox.max().y
        maxz = bbox.max().z

        # Getting points relative to the cameras transmformation matrix
        points.append(bbox.min() * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(maxx, miny, minz) * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(maxx, miny, maxz) * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(minx, miny, maxz) * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(minx, maxy, minz) * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(maxx, maxy, minz) * dWorldMtx * self.camInvWorldMtx)
        points.append(bbox.max() * dWorldMtx * self.camInvWorldMtx)
        points.append(OpenMaya.MPoint(minx, maxy, maxz) * dWorldMtx * self.camInvWorldMtx)

        relation = fnCam.relativeToFrustum(points)
        if relation:
            return True
        return False




import libmaya
import FrustrumScanner
# Can be optimised even more by sorting meshes by references, and then by removing all meshes from that reference if only one has been detected.

class FrustumScanner():

    def __init__(self, cameras, nodes):
        self.cameras = {}
        for camera in cameras:
            shotrange = [1, 100]
            self.cameras[camera] = {'inside': [],
                                    'outside': list(nodes),
                                    'range': shotrange
                                    }

    def objectsInCameraView(self, camera):
        # print 'test'
        for obj in list(self.cameras[camera]['outside']):
            if libmaya.isVisible(obj):
                CHK = frustrum.dkbObjectsInCameraView(camera, obj)
                if CHK.processNode():
                    self.cameras[camera]['inside'].append(obj)
                    self.cameras[camera]['outside'].remove(obj)
            else:
                print 'not visible'

    def processTimeline(self, begin=None, end=None, framePadding=1):
        if begin is None:
            begin = cmds.playbackOptions(query=True, minTime=True)
        if end is None:
            end = cmds.playbackOptions(query=True, maxTime=True)
        begin = int(begin)
        end = int(end)

        for frame in xrange(begin, end, framePadding):
            for camera in self.cameras:
                print self.cameras[camera]['range'][0], self.cameras[camera]['range'][1]
                if self.cameras[camera]['range'][0] <= frame <= self.cameras[camera]['range'][1]:
                    # Change the frame and scan only if needed
                    cmds.currentTime(frame)
                    self.objectsInCameraView(camera)

    def processCurrentFrame(self):
        current = cmds.currentTime(query=True)
        self.processTimeline(current, current + 1)




