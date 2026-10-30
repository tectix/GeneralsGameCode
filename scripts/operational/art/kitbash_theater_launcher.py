import sys, bpy, bmesh
sys.path.append(r"C:\Users\pc\AppData\Local\Programs\OpenSAGE.BlenderPlugin")
import io_mesh_w3d
io_mesh_w3d.register()
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_mesh.westwood_w3d(filepath=src)

rig = bpy.data.objects["AVTOMAHAWK"]
missile = bpy.data.objects["MISSILE"]
radar = bpy.data.objects["RADAR"]

def clone(obj, name, offset=(0, 0, 0), scale=(1, 1, 1)):
    c = obj.copy()
    c.data = obj.data.copy()
    c.name = name
    c.data.name = name
    bpy.context.scene.collection.objects.link(c)
    c.location = (obj.location[0] + offset[0], obj.location[1] + offset[1], obj.location[2] + offset[2])
    c.scale = (obj.scale[0] * scale[0], obj.scale[1] * scale[1], obj.scale[2] * scale[2])
    return c

# Second canister beside the missile, riding the elevating launcher.
clone(missile, "CANISTER02", offset=(0, 2.8, 0), scale=(1.05, 1.15, 1.15))
# Taller radar mast for the longer-range targeting role.
clone(radar, "RADAR02", offset=(0, 0, 3.0), scale=(1.4, 1.4, 1.4))

rig.name = "TCAVTHEATER"
rig.data.name = "TCAVTHEATER"
bpy.ops.export_mesh.westwood_w3d(filepath=dst, file_format='W3D', export_mode='HM')
print("EXPORTED", dst)
