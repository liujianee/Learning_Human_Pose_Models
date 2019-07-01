# ==============================================================================
# Author: Jian Liu
# Organization: The University of Western Australia
# Email: jian.liu@research.uwa.edu.au
# 
# This script is for the work: 
# "Learning Human Pose Models from Synthesized Data for Robust RGB-D Action Recognition" 
# https://arxiv.org/abs/1707.00823
# ==============================================================================

import sys
import bpy
import os
import math
import pickle
import shutil
import random
import numpy as np

print("=========================================")
print("pose starting from: ", sys.argv[5])
print("pose ending to: ", sys.argv[6])
print("=========================================")
# arguments passed into rendering batch
pose_start = int(sys.argv[5])
pose_end = int(sys.argv[6])

# define global variables
LIGHT_MODE = 1	# 0 - uniform lighting; 1 - random lighting
AMBIENT_ON = 1	# 1 - "use_ambient_occlusion"
VIEW_MODE = 0	# 0 - vertical rotation; 1 - spherical rotation
BB_OFFSET = 0.1 # max(0,random.gauss(2.0, 1.0))	# offset for bounding box

# pose representatives
poseFile = './poseReps4py'

# background images folder
bgPath = './source2/'
bgDirs = os.listdir(bgPath)

# texture images folder
uptexPath = './upper'
uptexFiles = os.listdir(uptexPath)
lowtexPath = './lower'
lowtexFiles = os.listdir(lowtexPath)

# mhx file
mhxFile = './MH.mhx'

# bvh file
bvhPath = './cmu_origin'

# save render result
saveDir = './results'
if not os.path.exists(saveDir):
    os.makedirs(saveDir)
    
def setBlender (lamppower):
    bpy.ops.object.mode_set(mode='OBJECT')
    # cleaning
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    #
    bpy.context.scene.world.use_sky_paper = True
    # add camera
    bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(0, -60, 2), rotation=(math.radians(90), 0, 0))
    bpy.context.scene.render.resolution_x = 640#2240#1920
    bpy.context.scene.render.resolution_y = 480#960
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.color_mode ='RGB'
    # add lamp
    setLamp ('AREA', (-15, -15, 10), 0, 'RECTANGLE', (0.1,0.1))
    setLamp ('AREA', (15, -15, 10), 0, 'RECTANGLE', (0.1,0.1))
    setLamp ('AREA', (0, -20, 10), 0, 'RECTANGLE', (0.1,0.1))
    # set ambient occlusion
    if AMBIENT_ON == 1:
        bpy.context.scene.world.light_settings.use_ambient_occlusion = True
        bpy.context.scene.world.light_settings.ao_factor = 0.2

def setLamp (type, location, strength, shape, size):
    bpy.ops.object.lamp_add(type=type, radius=1, view_align=False, location=location)
    name = bpy.context.active_object.data.name
    if type is 'AREA':
        bpy.data.lamps[name].shape = shape
        bpy.data.lamps[name].size = size[0]
        bpy.data.lamps[name].size_y = size[1]
    bpy.context.object.data.energy = strength

def setCamera (location):
    object = bpy.data.objects['Camera']
    bpy.context.scene.objects.active = object
    bpy.context.object.location[0] = location[0]
    bpy.context.object.location[1] = location[1]
    bpy.context.object.location[2] = location[2]
    
def setBackground (inputImage):
    img = bpy.data.images.load(inputImage)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = bpy.context.copy()
            override['area'] = area
            bpy.ops.view3d.background_image_remove(override, index=0)
            space_data = area.spaces.active
            space_data.show_background_images = True
            bg = space_data.background_images.new()
            bg.image = img
            break       
    
def setWorldTex (inputImage):
    img = bpy.data.images.load(inputImage)
    #bpy.ops.texture.new()
    bpy.data.textures["Texture"].image = img
    bpy.context.scene.world.active_texture = bpy.data.textures["Texture"]
    bpy.context.scene.world.texture_slots[0].use_map_horizon = True

def loadBody (bodyFile):
    bpy.ops.import_scene.makehuman_mhx(filter_glob="*.mhx", filepath=bodyFile)
    #bpy.ops.import_scene.makehuman_mhx2(filter_glob="*.mhx2", filepath=bodyFile)

def loadPose (startFrame, endFrame, objName, bvhFile):
    objActivate (objName)
    bpy.context.scene.McpStartFrame = startFrame
    bpy.context.scene.McpEndFrame = endFrame
    bpy.ops.mcp.load_and_retarget(filter_glob="*.bvh", filepath=bvhFile)
    # change from pose mode to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def selectFrame (frmNum):
    bpy.context.scene.frame_current = frmNum

def renderSave (saveFile):
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.data.scenes['Scene'].render.filepath = saveFile
    bpy.ops.render.render(write_still=True)
    
def objActivate (objName):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    object = bpy.data.objects[objName]
    bpy.context.scene.objects.active = object
    #object.select = True
       
def changeCloth (inputImage, objName):
    img = bpy.data.images.load(inputImage)
    # select an object whose texture is to be changes
    objActivate (objName)
    # change the image texture
    bpy.context.object.active_material.texture_slots[0].texture.image = img

# rotate body to get different viewpoints
def objRotate (object, rotation):
    object = bpy.data.objects[object]
    bpy.context.scene.objects.active = object
    bpy.context.object.pose.bones["master"].rotation_mode = 'ZYX'
    bpy.context.object.pose.bones["master"].rotation_euler[0] = math.radians(rotation[0])
    bpy.context.object.pose.bones["master"].rotation_euler[1] = math.radians(rotation[1])
    bpy.context.object.pose.bones["master"].rotation_euler[2] = math.radians(rotation[2])

# move body relative to the background
def objLocation (object, location):
    object = bpy.data.objects[object]
    bpy.context.scene.objects.active = object
    bpy.context.object.location[0] = location[0]
    bpy.context.object.location[1] = location[1]
    bpy.context.object.location[2] = location[2]


def getbbVertices (objInput):
	bbVertices = []
	boundBox = bpy.data.objects[objInput].bound_box
	for i in range(0,8):
	    vertex = [boundBox[i][0], boundBox[i][1], boundBox[i][2]]
	    bbVertices.append(vertex)
	return bbVertices

# to get the coordinates of bounding box
def getBounds (objInput, viewpoint, imgSize, camBorder):
    object = bpy.data.objects[objInput]
    objLoc = object.location
    objDim = object.dimensions
    camScale = bpy.context.scene.render.resolution_x/camBorder[0]
    bbVertices = getbbVertices(objInput)
    bbVertices = np.asarray(bbVertices)
    # to get min and max values along x- and z- axis, which surely enclose the body
    vertexMin = [np.min(bbVertices.transpose(1,0)[0]), np.min(bbVertices.transpose(1,0)[1]), np.min(bbVertices.transpose(1,0)[2])]
    vertexMax = [np.max(bbVertices.transpose(1,0)[0]), np.max(bbVertices.transpose(1,0)[1]), np.max(bbVertices.transpose(1,0)[2])]
    # offset is used to modify boundingbox manually
    offset = BB_OFFSET
    boundX = (camBorder[0]/2 + vertexMin[0] - offset) * camScale
    boundY = (camBorder[1]/2 - vertexMax[2] - offset) * camScale
    boundW = (vertexMax[0]-vertexMin[0] + 2*offset) * camScale
    boundH = (vertexMax[2]-vertexMin[2] + 2*offset) * camScale
    return [boundX, boundY, boundW, boundH]

'''def setEmpty ():
    bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=5, view_align=False, location=(0, 0, 0), rotation=(0, 0, 0))
    myempty = bpy.data.objects['Empty']
    mylamp_0 = bpy.data.objects['Point']
    mylamp_0.select = True
    for lampID in ['001','002','003','004','005','006','007']:
        lampname =  'Point.' +  lampID
        mylamp_i = bpy.data.objects[lampname]
        mylamp_i.select = True
    bpy.context.scene.objects.active = myempty
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    
def lampRotate(viewArgs):
    myempty = bpy.data.objects['Empty']
    bpy.context.scene.objects.active = myempty
    bpy.context.object.rotation_mode = 'ZYX'
    myempty.rotation_euler[0] = math.radians(viewArgs[0])
    myempty.rotation_euler[1] = math.radians(viewArgs[1])
    myempty.rotation_euler[2] = math.radians(viewArgs[2])'''

def lampEnergy(lampObj, energy):
    object = bpy.data.objects[lampObj]
    bpy.context.scene.objects.active = object
    bpy.context.object.data.energy = energy
    bpy.context.object.data.shadow_method = 'RAY_SHADOW'
  

# Main program starts here
with open(poseFile, 'rb') as f:
    poseList = pickle.load(f)


if LIGHT_MODE == 0:
    lamppower = [15,15,15,15,15,15,15,15]
elif LIGHT_MODE == 1:
    # randomly generate lamp power, and then mask some of them
    lamppower = random.sample(range(0, 15), 8)
    lampmask = random.sample(range(0, 8),random.randint(0,8))
    for m in lampmask:
        lamppower[m] = 0


setBlender(lamppower)
setCamera((0, -40, 0))  # to match 640*480 background
loadBody(mhxFile)


# different view points
HORI_STEPS = 24
VERT_STEPS = 4

viewList = []
#for pp in range(0, HORI_STEPS):
for pp in range(-3, 4):
    phi = -pp * 15
    for tt in range (0, VERT_STEPS):
        theta = tt * 15
        myview = (theta, 0, phi)
        viewList.append(myview)

# here are the objects to be manipulated
clothList = ['MH:tshirt02', 'MH:jeans01']
objShirt = clothList[0]
objJeans = clothList[1]
objModel = 'MH'
objBody = 'MH:Body'

imgSize = [640, 480]
camBorder = [35.5, 26.5]

# create one texture, so function "setWorldTex" can change its image
bpy.ops.texture.new()

#boundList = []
for poseIter in range(pose_start,pose_end):
    fileList = []
    paramList = []
    h = poseIter
    thePose = poseList[h]
    bvhFile = bvhPath + '/' + thePose[0]
    # frame number is different between bvh and blender
    frame = int(thePose[1]/5)
    loadPose(frame, frame, objModel, bvhFile)
    selectFrame(1)
    poseDir = saveDir + '/' + 'pose' + str(h)
    if not os.path.exists(poseDir):
    	os.makedirs(poseDir)    
    for num in range(0, 5):
        k = 0
        # change background
        bgDir = random.choice(bgDirs)
        # change cloth texture
        uptexFile = random.choice(uptexFiles)
        texImage = uptexPath +'/' + uptexFile
        changeCloth (texImage, objShirt)
        lowtexFile = random.choice(lowtexFiles)
        texImage = lowtexPath +'/' + lowtexFile
        changeCloth (texImage, objJeans)
        for viewpoint in viewList:
            k += 1
            if VIEW_MODE == 0:
                bgID = (k-1) % VERT_STEPS # stepping according to viewlist
            elif VIEW_MODE == 1:
                bgID = k-1
            bgFile = bgDir + '_view' + str(bgID+1) + '.png' # senstive to background files' name
            bgImage = bgPath + bgDir + '/' + bgFile
            setWorldTex (bgImage)
            objRotate (objModel, viewpoint)
            lamp_select = random.randint(0, 2)
            lamp_energy = random.uniform(0.5, 1.5)
            if lamp_select == 0:
                lampEnergy('Area', lamp_energy)
            if lamp_select == 1:
                lampEnergy('Area.001', lamp_energy)
            if lamp_select == 1:
                lampEnergy('Area.002', lamp_energy)
            saveFile = (poseDir + '/' + 'rl_pose' + str(h) + '_idx' + str(num) + '_view' + str(k))
            renderSave (saveFile)
            [boundX, boundY, boundW, boundH] = getBounds(objBody, viewpoint, imgSize, camBorder)
            boundParam = [boundX, boundY, boundW, boundH]
            fileList.append(saveFile)
            paramList.append(boundParam)
    fileArr = np.asarray(fileList)
    paramArr = np.asarray(paramList)
    fileNpy = poseDir + '/filelist.npy'
    np.save( fileNpy , fileArr )
    paramNpy = poseDir + '/bbparams.npy'
    np.save( paramNpy , paramArr )
