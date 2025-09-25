#import bpy

#frame1 = {'x4': 765.315995, 'y4': 152.2198641,
#            'x5': 999.9523507, 'y5': 267.9216821}
#            
#point1 = (frame1['x4'], frame1['y4'], 0.0)
#point2 = (frame1['x5'], frame1['y5'], 0.0)

## === Plot the Points === #

#def plot_point(name, location):
#    bpy.ops.mesh.primitive_uv_sphere_add(radius=5.0, location=location)
#    bpy.context.active_object.name = name
#    
#plot_point("Node4", point1)
#plot_point("Node5", point2)

#def create_curve(p1, p2, name="InterpolatedLine"):
#    curve_data = bpy.data.curves.new(name=name, type='CURVE')
#    curve_data.dimensions = '3D'
#    
#    polyline = curve_data.splines.new('POLY')
#    polyline.points.add(1)
#    polyline.points[0].co = (*p1, 1)
#    polyline.points[1].co = (*p2, 1)
#    
#    curve_obj = bpy.data.objects.new(name, curve_data)
#    bpy.context.collection.objects.link(curve_obj)

#create_curve(point1, point2)

            
#import bpy
#import mathutils

## === STEP 1: Define Points ===
#point1 = mathutils.Vector((765.315995, 152.2198641, 0.0))
#point2 = mathutils.Vector((999.9523507, 267.9216821, 0.0))

## === STEP 2: Compute Direction and Midpoint ===
#direction = point2 - point1
#length = direction.length
#midpoint = (point1 + point2) / 2
#axis = direction.normalized()

## === STEP 3: Create Cylinder ===
#bpy.ops.mesh.primitive_cylinder_add(
#    radius=5.0,
#    depth=length,
#    location=(0, 0, 0)
#)
#cylinder = bpy.context.active_object
#cylinder.name = "ConnectorPipe"

## === STEP 4: Align Cylinder to Direction Vector ===
#z_axis = mathutils.Vector((0, 0, 1))
#rot_quat = z_axis.rotation_difference(direction)
#cylinder.rotation_mode = 'QUATERNION'
#cylinder.rotation_quaternion = rot_quat

## === STEP 5: Move Cylinder to Midpoint ===
#cylinder.location = midpoint

## === STEP 6: Add Arrow to Represent Axis ===
#arrow_length = 50.0
#arrow_radius = 3.0
#bpy.ops.mesh.primitive_cone_add(
#    radius1=arrow_radius,
#    depth=arrow_length,
#    location=(0, 0, 0)
#)
#arrow = bpy.context.active_object
#arrow.name = "AxisArrow"

## Align arrow (same rotation as pipe)
#arrow.rotation_mode = 'QUATERNION'
#arrow.rotation_quaternion = rot_quat

## Move arrow to extend out from the pipe's top end
#offset = axis * (length / 2 + arrow_length / 2)
#arrow.location = midpoint + offset

#import bpy
#import math
#import mathutils

## === Variables to be Updated by Socket Communication ==
#point1 = mathutils.Vector((765.315995, 152.2198641, 0.0))
#point2 = mathutils.Vector((999.9523507, 267.9216821, 0.0))
#point1rot = 9.979
#point2rot = 7.983

## === MAIN LOOP === #

#cyldSpinRate = ( (point1rot + point2rot) / 2 )
#cyldRPM = cyldSpinRate * (60 / (2*math.pi))

## === STEP 1: Compute Direction and Midpoint ===
#direction = point2 - point1
#length = direction.length
#midpoint = (point1 + point2) / 2
#axis = direction.normalized()

## === STEP 2: Create Cylinder ===
#bpy.ops.mesh.primitive_cylinder_add(
#    radius=5.0,
#    depth=length,
#    location=(0, 0, 0)
#)
#cylinder = bpy.context.active_object
#cylinder.name = "ConnectorPipe"
#cylinder.rotation_mode = 'QUATERNION'

## === STEP 3: Align Cylinder to Axis ===
#z_axis = mathutils.Vector((0, 0, 1))
#align_quat = z_axis.rotation_difference(axis)
#cylinder.rotation_quaternion = align_quat
#cylinder.location = midpoint

## === STEP 4: Add Axis Arrow ===
#arrow_length = 50.0
#arrow_radius = 3.0
#bpy.ops.mesh.primitive_cone_add(
#    radius1=arrow_radius,
#    depth=arrow_length,
#    location=(0, 0, 0)
#)
#arrow = bpy.context.active_object
#arrow.name = "AxisArrow"
#arrow.rotation_mode = 'QUATERNION'
#arrow.rotation_quaternion = align_quat
#arrow.location = midpoint + axis * (length / 2 + arrow_length / 2)
#arrow.parent = cylinder
#arrow.matrix_parent_inverse = cylinder.matrix_world.inverted()

## === STEP 5: Animate Cylinder Spin Around Its Own Axis ===
#cylinder.animation_data_clear()

#start_frame = 1
#end_frame = 250
#rpm = cyldRPM
#rps = rpm / 60
#angle_per_frame = (2 * math.pi * rps) / 24  # radians per frame

#for frame in range(start_frame, end_frame + 1):
#    bpy.context.scene.frame_set(frame)
#    
#    # Total spin angle
#    spin_angle = angle_per_frame * (frame - start_frame)

#    # Build spin quaternion around local axis
#    spin_quat = mathutils.Quaternion(z_axis, spin_angle)

#    # Combine alignment with spin
#    final_quat = align_quat @ spin_quat

#    cylinder.rotation_quaternion = final_quat
#    cylinder.keyframe_insert(data_path="rotation_quaternion")
    
# END OF LOOP #
    
## === Add Camera Watching the Drill Bit End ===

## Create a new camera
#bpy.ops.object.camera_add()
#camera = bpy.context.active_object
#camera.name = "DrillCam"

## Offset camera from the drill bit end (point2)
## This offset goes: 100 units up, 100 units to the right, and 100 units back along the axis
#up_offset = mathutils.Vector((0, 0, 100))
#side_offset = axis.cross(up_offset).normalized() * 100
#back_offset = -axis.normalized() * 100
#cam_position = point2 + up_offset + side_offset + back_offset
#camera.location = cam_position

## Make the camera look at point2 (the drill bit end)
#direction_to_target = point2 - cam_position
#rot_quat = direction_to_target.to_track_quat('-Z', 'Y')  # Camera looks along -Z
#camera.rotation_mode = 'QUATERNION'
#camera.rotation_quaternion = rot_quat

## Set this camera as the active camera
#bpy.context.scene.camera = camera

import bpy
import math
import mathutils
import socket
import threading
import json
import os

# === Global Camera Flag ===
camera_initialized = False

# === Drill Target ===
## Run once to create the drilling surface
#if "DrillTarget" not in bpy.data.objects:
#    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, 0))
#    drill_surface = bpy.context.active_object
#    drill_surface.name = "DrillTarget"
#else:
#    drill_surface = bpy.data.objects["DrillTarget"]
#    
#### === Move Drill Target to Simulate Movement ===
#start_frame = 1
#end_frame = 250
#movement_per_frame = 0.02
#drill_surface.animation_data_clear()

#for frame in range(start_frame, end_frame + 1):
#    bpy.context.scene.frame_set(frame)
#    drill_surface.location.x = (frame - start_frame) * movement_per_frame
#    drill_surface.keyframe_insert(data_path="location", index=0)

#action = drill_surface.animation_data.action
#for fcurve in action.fcurves:
#    for keyframe in fcurve.keyframe_points:
#        keyframe.interpolation = 'LINEAR'

## Ensure the DrillTarget exists
#drill_surface = bpy.data.objects.get("DrillTarget")
#if not drill_surface:
#    bpy.ops.mesh.primitive_plane_add(size=500, location=(850, 200, 0))
#    drill_surface = bpy.context.active_object
#    drill_surface.name = "DrillTarget"

## Create a new material
#material = bpy.data.materials.get("DrillTextureMat")
#if not material:
#    material = bpy.data.materials.new(name="DrillTextureMat")
#    material.use_nodes = True

## Assign the material to the drill surface
#if drill_surface.data.materials:
#    drill_surface.data.materials[0] = material
#else:
#    drill_surface.data.materials.append(material)

## Load the texture image
#image_path = "/Users/jaymarch/Documents/Summer 2025 Research/Summer-2025-Research/Rock031_4K-JPG_Color.jpg"  # Replace with your actual file path
#image = bpy.data.images.load(image_path)

## Get the material's node tree
#nodes = material.node_tree.nodes
#links = material.node_tree.links

## Clear default nodes
#for node in nodes:
#    nodes.remove(node)

## Create nodes
#tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
#mapping_node = nodes.new(type='ShaderNodeMapping')
#image_node = nodes.new(type='ShaderNodeTexImage')
#bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
#output_node = nodes.new(type='ShaderNodeOutputMaterial')

## Connect nodes
#image_node.image = image
#links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
#links.new(mapping_node.outputs['Vector'], image_node.inputs['Vector'])
#links.new(image_node.outputs['Color'], bsdf_node.inputs['Base Color'])
#links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

## Scroll rate (change to make texture scroll faster/slower)
#scroll_rate = 0.001  # units per frame

## Animate the Mapping Node's translation X value
#for frame in range(1, 251):
#    mapping_node.inputs['Location'].default_value[0] = frame * scroll_rate  # X
#    mapping_node.inputs['Location'].default_value[1] = frame * scroll_rate  # Y
#    mapping_node.inputs['Location'].keyframe_insert(data_path="default_value", index=0, frame=frame)
#    mapping_node.inputs['Location'].keyframe_insert(data_path="default_value", index=1, frame=frame)
#    
## Optional: make interpolation linear (no ease in/out)
#for fcurve in material.node_tree.animation_data.action.fcurves:
#    for keyframe in fcurve.keyframe_points:
#        keyframe.interpolation = 'LINEAR'

## === DrillTarget Setup (runs once and stays untouched) ===
#drill_surface = bpy.data.objects.get("DrillTarget")
#if not drill_surface:
#    bpy.ops.mesh.primitive_plane_add(size=500, location=(850, 200, 0))
#    drill_surface = bpy.context.active_object
#    drill_surface.name = "DrillTarget"

#    # Add UVs
#    bpy.ops.object.mode_set(mode='EDIT')
#    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
#    bpy.ops.object.mode_set(mode='OBJECT')

#    # Lock transformations to prevent deletion or movement
#    drill_surface.hide_select = True
#    drill_surface.lock_location = (True, True, True)
#    drill_surface.lock_rotation = (True, True, True)
#    drill_surface.lock_scale = (True, True, True)

## === Load rock texture maps ===
#base_color_img = bpy.data.images.load("/Users/jaymarch/Documents/Summer 2025 Research/Summer-2025-Research/Rock031.png")
#roughness_img = bpy.data.images.load("/Users/jaymarch/Documents/Summer 2025 Research/Summer-2025-Research/Rock031_4K-JPG_Roughness.jpg")
#normal_img = bpy.data.images.load("/Users/jaymarch/Documents/Summer 2025 Research/Summer-2025-Research/Rock031_4K-JPG_NormalGL.jpg")
#ao_img = bpy.data.images.load("/Users/jaymarch/Documents/Summer 2025 Research/Summer-2025-Research/Rock031_4K-JPG_AmbientOcclusion.jpg")

## === Create rock material ===
#rock_mat = bpy.data.materials.new(name="RockMaterial")
#rock_mat.use_nodes = True
#nodes = rock_mat.node_tree.nodes
#links = rock_mat.node_tree.links
#nodes.clear()

## === Create and connect shader nodes ===
#output_node = nodes.new("ShaderNodeOutputMaterial")
#bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
#tex_base = nodes.new("ShaderNodeTexImage"); tex_base.image = base_color_img
#tex_rough = nodes.new("ShaderNodeTexImage"); tex_rough.image = roughness_img
#tex_normal = nodes.new("ShaderNodeTexImage"); tex_normal.image = normal_img; tex_normal.image.colorspace_settings.name = 'Non-Color'
#tex_ao = nodes.new("ShaderNodeTexImage"); tex_ao.image = ao_img; tex_ao.image.colorspace_settings.name = 'Non-Color'
#normal_map_node = nodes.new("ShaderNodeNormalMap")
#ao_mix = nodes.new("ShaderNodeMixRGB"); ao_mix.blend_type = 'MULTIPLY'; ao_mix.inputs['Fac'].default_value = 1.0
#tex_coord = nodes.new("ShaderNodeTexCoord")
#mapping = nodes.new("ShaderNodeMapping")

## Texture mapping
#links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
#for tex in [tex_base, tex_rough, tex_normal, tex_ao]:
#    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])

## Shader connections
#links.new(tex_base.outputs["Color"], ao_mix.inputs[1])
#links.new(tex_ao.outputs["Color"], ao_mix.inputs[2])
#links.new(ao_mix.outputs["Color"], bsdf_node.inputs["Base Color"])
#links.new(tex_rough.outputs["Color"], bsdf_node.inputs["Roughness"])
#links.new(tex_normal.outputs["Color"], normal_map_node.inputs["Color"])
#links.new(normal_map_node.outputs["Normal"], bsdf_node.inputs["Normal"])
#links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

## === Apply material to DrillTarget ===
#drill_surface.data.materials.clear()
#drill_surface.data.materials.append(rock_mat)

# === Ensure the DrillTarget exists ===
drill_surface = bpy.data.objects.get("DrillTarget")
if not drill_surface:
    bpy.ops.mesh.primitive_plane_add(size=500, location=(850, 200, 0))
    drill_surface = bpy.context.active_object
    drill_surface.name = "DrillTarget"

    # Add UV unwrap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

# === Load texture maps ===
base_color_img = bpy.data.images.load(r"C:\Users\marchjay\Documents\Summer-2025-Research-main\Rock031.png")
roughness_img = bpy.data.images.load(r"C:\Users\marchjay\Documents\Summer-2025-Research-main\Rock031_4K-JPG_Roughness.jpg")
normal_img = bpy.data.images.load(r"C:\Users\marchjay\Documents\Summer-2025-Research-main\Rock031_4K-JPG_NormalGL.jpg")
ao_img = bpy.data.images.load(r"C:\Users\marchjay\Documents\Summer-2025-Research-main\Rock031_4K-JPG_AmbientOcclusion.jpg")

# === Create or get the material ===
material = bpy.data.materials.get("DrillTextureMat")
if not material:
    material = bpy.data.materials.new(name="DrillTextureMat")
    material.use_nodes = True

# === Assign material to drill surface ===
if drill_surface.data.materials:
    drill_surface.data.materials[0] = material
else:
    drill_surface.data.materials.append(material)

# === Node setup ===
nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

# Nodes
tex_coord = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeMapping")
tex_base = nodes.new("ShaderNodeTexImage")
tex_base.image = base_color_img

tex_rough = nodes.new("ShaderNodeTexImage")
tex_rough.image = roughness_img
tex_rough.image.colorspace_settings.name = 'Non-Color'

tex_normal = nodes.new("ShaderNodeTexImage")
tex_normal.image = normal_img
tex_normal.image.colorspace_settings.name = 'Non-Color'

tex_ao = nodes.new("ShaderNodeTexImage")
tex_ao.image = ao_img
tex_ao.image.colorspace_settings.name = 'Non-Color'

normal_map = nodes.new("ShaderNodeNormalMap")
ao_mix = nodes.new("ShaderNodeMixRGB")
ao_mix.blend_type = 'MULTIPLY'
ao_mix.inputs['Fac'].default_value = 1.0

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
output = nodes.new("ShaderNodeOutputMaterial")

# Connect Mapping to all texture nodes
links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
for tex in [tex_base, tex_rough, tex_normal, tex_ao]:
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])

# AO + BaseColor to BSDF base color
links.new(tex_base.outputs["Color"], ao_mix.inputs[1])
links.new(tex_ao.outputs["Color"], ao_mix.inputs[2])
links.new(ao_mix.outputs["Color"], bsdf.inputs["Base Color"])

# Roughness
links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])

# Normal
links.new(tex_normal.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

# Final output
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

# === Animate Mapping Scroll ===
scroll_rate = 0.001
for frame in range(1, 251):
    mapping.inputs['Location'].default_value[0] = frame * scroll_rate
    mapping.inputs['Location'].default_value[1] = frame * scroll_rate
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", index=0, frame=frame)
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", index=1, frame=frame)

# Linear keyframes
if material.node_tree.animation_data:
    for fcurve in material.node_tree.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

# === Function to Build a Frame from Incoming Data ===
def update_frame(point1, point2, point1rot, point2rot):
    # === Clear previous geometry ===
    for obj in bpy.data.objects:
        if obj.name.startswith("ConnectorPipe"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # === Compute Rotation Speed ===
    cyldSpinRate = (point1rot + point2rot) / 2
    cyldRPM = cyldSpinRate * (60 / (2 * math.pi))

    # === Geometry Calculations ===
    direction = point2 - point1
    length = direction.length
    midpoint = (point1 + point2) / 2
    axis = direction.normalized()

    # === Create Cylinder ===
    bpy.ops.mesh.primitive_cylinder_add(radius=5.0, depth=length, location=(0, 0, 0))
    cylinder = bpy.context.active_object
    cylinder.name = "ConnectorPipe"
    cylinder.rotation_mode = 'QUATERNION'
    
    # === Assign Metal Like Material to the Cylinder ===
    # === Create or get a metal material ===
    metal_mat = bpy.data.materials.get("MetalMaterial")
    if not metal_mat:
        metal_mat = bpy.data.materials.new(name="MetalMaterial")
        metal_mat.use_nodes = True

        nodes = metal_mat.node_tree.nodes
        links = metal_mat.node_tree.links

        while nodes:
            nodes.remove(nodes[0])

        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

        bsdf_node.inputs['Metallic'].default_value = 1.0
        bsdf_node.inputs['Roughness'].default_value = 0.2
        bsdf_node.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1)

    # === Assign material to cylinder ===
    if len(cylinder.data.materials) == 0:
        cylinder.data.materials.append(metal_mat)
    else:
        cylinder.data.materials[0] = metal_mat

    z_axis = mathutils.Vector((0, 0, 1))
    x_axis = mathutils.Vector((1, 0, 0))
    align_quat = z_axis.rotation_difference(axis)
    pdc_quat = x_axis.rotation_difference(axis)
    cylinder.rotation_quaternion = align_quat
    cylinder.location = midpoint

#    # === Create Axis Arrow ===
#    arrow_length = 50.0
#    bpy.ops.mesh.primitive_cone_add(radius1=3.0, depth=arrow_length, location=(0, 0, 0))
#    arrow = bpy.context.active_object
#    arrow.name = "AxisArrow"
#    arrow.rotation_mode = 'QUATERNION'
#    arrow.rotation_quaternion = align_quat
#    arrow.location = midpoint + axis * (length / 2 + arrow_length / 2)
#    arrow.parent = cylinder
#    arrow.matrix_parent_inverse = cylinder.matrix_world.inverted()
#    apply_discrete_torque_color(arrow, cyldSpinRate)

    # === Remove old PDC instances ===
    for obj in bpy.data.objects:
        if obj.name.startswith("PDC") and obj.name != "PDC":
            bpy.data.objects.remove(obj, do_unlink=True)

    # === Attach PDC Bit === 
    pdc_template = bpy.data.objects.get("PDC")
    if pdc_template:
        # Duplicate PDC and link to scene
        pdc = pdc_template.copy()
        pdc.data = pdc_template.data.copy()
        bpy.context.collection.objects.link(pdc)
        
                # === Assign metal material to PDC
        if len(pdc.data.materials) == 0:
            pdc.data.materials.append(metal_mat)
        else:
            pdc.data.materials[0] = metal_mat

        # Scale PDC (optional)
        pdc.scale = (0.39, 0.39, 0.39)

        pdc.rotation_mode = 'QUATERNION'
        pdc.rotation_quaternion = pdc_quat

        # Compute world matrix using translation and rotation
        pdc.location = midpoint + axis * (length / 2)

        # Parent to cylinder (preserve transform)
#        pdc.parent = cylinder
#        pdc.matrix_parent_inverse = cylinder.matrix_world.inverted()
    
    # === Create singular instance of Camera ===
#    global camera_initialized
#    if not camera_initialized:
#        initialize_camera(point2, axis)
#        camera_initialized = True

    # === Animate Cylinder Spin ===
    cylinder.animation_data_clear()
    pdc.animation_data_clear()
    start_frame = 1
    end_frame = 250
    rps = cyldRPM / 60
    angle_per_frame = (2 * math.pi * rps) / 24
#    depth_per_frame = 0.1

    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        spin_angle = angle_per_frame * (frame - start_frame)
        spin_quat = mathutils.Quaternion(z_axis, spin_angle)
        final_quat = align_quat @ spin_quat
        cylinder.rotation_quaternion = final_quat
        cylinder.keyframe_insert(data_path="rotation_quaternion")
        # Rotate the PDC bit to match the same spinning behavior
        pdc_spin_quat = mathutils.Quaternion(x_axis, spin_angle)
        pdc_final_quat = pdc_quat @ pdc_spin_quat
        pdc.rotation_quaternion = pdc_final_quat
        pdc.keyframe_insert(data_path="rotation_quaternion")
        
#        # --- Forward Motion Along Axis (Impact Drilling) ---
#        depth_offset = axis * (frame * depth_per_frame)
#        cylinder.location = midpoint + depth_offset
#        pdc.location = (midpoint + axis * (length / 2)) + depth_offset
#        cylinder.keyframe_insert(data_path="location")
#        pdc.keyframe_insert(data_path="location")

    print(f"✅ Frame built from: p1={point1}, p2={point2}, rpm={cyldRPM:.2f}") 
    
## === Function to initialize Camera based of inital drill bit position ===
#def initialize_camera(drill_tip, axis):
#    bpy.ops.object.camera_add()
#    camera = bpy.context.active_object
#    camera.name = "DrillCam"

#    # Place the camera slightly above, to the side, and back from the drill bit
#    up_offset = mathutils.Vector((0, 0, 100))
#    side_offset = axis.cross(up_offset).normalized() * 400
#    back_offset = -axis.normalized() * 50

##    front_offset = axis.normalized() * 150
##    up_offset = mathutils.Vector((0, 0, 40))
##    side_offset = axis.cross(up_offset).normalized() * 400

#    cam_position = drill_tip + up_offset + side_offset + back_offset
#    camera.location = cam_position

#    # Point camera at the drill bit
#    direction_to_target = drill_tip - cam_position
#    rot_quat = direction_to_target.to_track_quat('-Z', 'Y')
#    camera.rotation_mode = 'QUATERNION'
#    camera.rotation_quaternion = rot_quat
#    
##    camera.data.lens = 35

#    bpy.context.scene.camera = camera
#    print("🎥 Camera initialized at first frame.")
    
## === Function to Color Map Arrow to cyldSpinRate
#def apply_discrete_torque_color(obj, cyldSpinRate):
#    # Define color based on torque ranges
#    if cyldSpinRate < 8:
#        color = (0.0, 0.0, 1.0, 1.0)  # Blue
#    elif cyldSpinRate < 10:
#        color = (0.0, 1.0, 0.0, 1.0)  # Green
#    elif cyldSpinRate < 12:
#        color = (1.0, 0.5, 0.0, 1.0)  # Orange
#    else:
#        color = (1.0, 0.0, 0.0, 1.0)  # Red

#    # Create an emission material
#    mat = bpy.data.materials.new(name="TorqueColor")
#    mat.use_nodes = True
#    nodes = mat.node_tree.nodes
#    links = mat.node_tree.links

#    # Clear existing nodes
#    while nodes:
#        nodes.remove(nodes[0])

#    output = nodes.new(type='ShaderNodeOutputMaterial')
#    emission = nodes.new(type='ShaderNodeEmission')
#    emission.inputs['Color'].default_value = color
#    emission.inputs['Strength'].default_value = 1.0

#    links.new(emission.outputs['Emission'], output.inputs['Surface'])

#    # Apply material
#    if obj.data.materials:
#        obj.data.materials[0] = mat
#    else:
#        obj.data.materials.append(mat)
#    print(cyldSpinRate)
#    print(color)

# === TCP Socket Server to Receive JSON Frame Data ===
def socket_server():
    HOST = 'localhost'
    PORT = 13000
    print(f"🟢 Listening for frame data on {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, _ = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    decoded = data.decode().strip()
                    if not decoded:
                        continue
                    frame_data = json.loads(decoded)
                    
                    # Find all node indices
                    node_indices = sorted(set(int(k[1:]) for k in frame_data.keys() if k.startswith('x')))

                    if len(node_indices) < 2:
                        raise ValueError("Not enough nodes in frame_data")

                    second_last = node_indices[-2]
                    last = node_indices[-1]

                    # Parse and convert incoming data
                    p1 = mathutils.Vector((
                        float(frame_data[f'x{second_last}'] + 10),
                        float(frame_data[f'y{second_last}'] + 10),
                        0.0
                        ))
                        
                    p2 = mathutils.Vector((
                        float(frame_data[f'x{last}'] + 100),
                        float(frame_data[f'y{last}'] + 100),
                        0.0
                        ))
                        
                    rot1 = float(frame_data[f'rot{second_last}'])
                    rot2 = float(frame_data[f'rot{last}'] + 10)

#                    # Parse and convert incoming data
#                    p1 = mathutils.Vector((float(frame_data['x4']), float(frame_data['y4']), 0.0))
#                    p2 = mathutils.Vector((float(frame_data['x5']), float(frame_data['y5']), 0.0))
#                    rot1 = float(frame_data['rot4'])
#                    rot2 = float(frame_data['rot5'])

                    # Call Blender-safe update using timer
                    def call_update():
                        update_frame(p1, p2, rot1, rot2)
                        return None

                    bpy.app.timers.register(call_update, first_interval=0.01)

                except Exception as e:
                    print(f"❌ Failed to parse or update frame: {e}")


# === Start TCP Server on Background Thread ===
threading.Thread(target=socket_server, daemon=True).start()
print("🚀 Blender TCP update system initialized.")

