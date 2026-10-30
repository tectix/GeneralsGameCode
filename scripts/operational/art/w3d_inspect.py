import sys, bpy
sys.path.append(r"C:\Users\pc\AppData\Local\Programs\OpenSAGE.BlenderPlugin")
import io_mesh_w3d
io_mesh_w3d.register()
src = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_mesh.westwood_w3d(filepath=src)
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    dims = tuple(round(d, 1) for d in o.dimensions)
    parent = o.parent.name if o.parent else "-"
    extra = ""
    if o.type == 'MESH':
        extra = f"verts={len(o.data.vertices)} mats={[m.name for m in o.data.materials]}"
    print(f"OBJ {o.type:8} {o.name:28} parent={parent:16} bone={o.parent_bone or '-':14} dims={dims} {extra}")
for a in bpy.data.armatures:
    print("ARMATURE", a.name, [b.name for b in a.bones])
for img in bpy.data.images:
    print("IMAGE", img.name, img.filepath)
