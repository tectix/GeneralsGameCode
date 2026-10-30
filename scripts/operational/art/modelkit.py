"""Helpers for building original W3D models in headless Blender.

Geometry is built with bmesh, UVs are box-projected from world space so textures tile at a
constant density, and textures are generated with numpy and saved as TGA next to the model.
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

PLUGIN_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "OpenSAGE.BlenderPlugin")


def start_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if PLUGIN_DIR not in sys.path:
        sys.path.append(PLUGIN_DIR)
    import io_mesh_w3d
    try:
        io_mesh_w3d.register()
    except ValueError:
        pass  # already registered


# --------------------------------------------------------------------------------------------
# Textures
# --------------------------------------------------------------------------------------------

def _value_noise(size, cells, rng):
    grid = rng.random((cells + 1, cells + 1))
    grid[-1, :] = grid[0, :]
    grid[:, -1] = grid[:, 0]
    coords = np.linspace(0, cells, size, endpoint=False)
    i = coords.astype(int)
    f = coords - i
    f = f * f * (3 - 2 * f)
    a = grid[np.ix_(i, i)]
    b = grid[np.ix_(i, i + 1)]
    c = grid[np.ix_(i + 1, i)]
    d = grid[np.ix_(i + 1, i + 1)]
    fx = f[None, :]
    fy = f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fractal_noise(size, seed, octaves=5, base_cells=4):
    rng = np.random.default_rng(seed)
    total = np.zeros((size, size))
    amplitude, norm = 1.0, 0.0
    for octave in range(octaves):
        total += amplitude * _value_noise(size, base_cells * 2 ** octave, rng)
        norm += amplitude
        amplitude *= 0.5
    return total / norm


def make_texture(name, out_dir, base_rgb, size=512, seed=1, grime=0.35, speckle=0.06,
                 panel_lines=0, line_darkness=0.35, streaks=0.0):
    """Tileable surface texture: base color, large-scale grime, fine speckle, optional panel
    seams and vertical rain streaks."""
    base = np.array(base_rgb, dtype=float)
    large = fractal_noise(size, seed, octaves=4, base_cells=3)
    fine = fractal_noise(size, seed + 7, octaves=3, base_cells=32)
    shade = 1.0 - grime * (large - 0.5) * 2.0 * 0.5 - speckle * (fine - 0.5) * 2.0

    if panel_lines:
        step = size // panel_lines
        lines = np.ones((size, size))
        for k in range(panel_lines):
            p = k * step
            lines[:, p:p + 2] *= 1.0 - line_darkness
            lines[p:p + 2, :] *= 1.0 - line_darkness
        shade *= lines

    if streaks > 0.0:
        rng = np.random.default_rng(seed + 13)
        column = rng.random(size) ** 6
        fade = np.linspace(1.0, 0.2, size)[:, None]
        shade *= 1.0 - streaks * column[None, :] * fade

    rgb = np.clip(base[None, None, :] * shade[:, :, None], 0.0, 1.0)
    rgba = np.concatenate([rgb, np.ones((size, size, 1))], axis=2)

    image = bpy.data.images.new(name, size, size, alpha=False)
    image.pixels.foreach_set(rgba[::-1].astype(np.float32).ravel())
    path = os.path.join(out_dir, name + ".tga")
    settings = bpy.context.scene.render.image_settings
    settings.file_format = "TARGA"
    settings.color_mode = "RGB"
    image.save_render(path)
    return image


def make_material(name, image, emissive=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.75
    if emissive:
        bsdf.inputs["Emission Color"].default_value = (*emissive, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat


# --------------------------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------------------------

class Builder:
    """Accumulates parts into one bmesh per output object, tagging faces with material slots."""

    def __init__(self, name, uv_scale=40.0):
        self.name = name
        self.uv_scale = uv_scale
        self.bm = bmesh.new()
        self.materials = []

    def _slot(self, material):
        if material not in self.materials:
            self.materials.append(material)
        return self.materials.index(material)

    def _add(self, temp, material, matrix):
        bmesh.ops.transform(temp, matrix=matrix, verts=temp.verts)
        slot = self._slot(material)
        for face in temp.faces:
            face.material_index = slot
        mesh = bpy.data.meshes.new("tmp")
        temp.to_mesh(mesh)
        temp.free()
        self.bm.from_mesh(mesh)
        bpy.data.meshes.remove(mesh)

    def box(self, material, size, location=(0, 0, 0), rotation=(0, 0, 0), bevel=0.0):
        temp = bmesh.new()
        bmesh.ops.create_cube(temp, size=1.0)
        bmesh.ops.scale(temp, vec=Vector(size), verts=temp.verts)
        if bevel > 0.0:
            bmesh.ops.bevel(temp, geom=list(temp.edges), offset=bevel, segments=2, affect="EDGES", profile=0.5)
        self._add(temp, material, _matrix(location, rotation))

    def hull(self, material, points, location=(0, 0, 0), rotation=(0, 0, 0)):
        temp = bmesh.new()
        verts = [temp.verts.new(p) for p in points]
        bmesh.ops.convex_hull(temp, input=verts)
        self._add(temp, material, _matrix(location, rotation))

    def cylinder(self, material, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), segments=16, radius_top=None):
        temp = bmesh.new()
        bmesh.ops.create_cone(temp, cap_ends=True, segments=segments, radius1=radius,
                              radius2=radius if radius_top is None else radius_top, depth=depth)
        self._add(temp, material, _matrix(location, rotation))

    def dish(self, material, radius, depth, location=(0, 0, 0), rotation=(0, 0, 0), segments=24):
        temp = bmesh.new()
        bmesh.ops.create_uvsphere(temp, u_segments=segments, v_segments=12, radius=1.0)
        bmesh.ops.delete(temp, geom=[v for v in temp.verts if v.co.z > 0.05], context="VERTS")
        bmesh.ops.scale(temp, vec=Vector((radius, radius, depth)), verts=temp.verts)
        self._add(temp, material, _matrix(location, rotation))

    def build(self, parent=None):
        mesh = bpy.data.meshes.new(self.name)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        box_project_uvs(self.bm, scale=self.uv_scale)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for material in self.materials:
            mesh.materials.append(material)
        obj = bpy.data.objects.new(self.name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        if parent is not None:
            obj.parent = parent
        return obj


def _matrix(location, rotation):
    rot = Matrix.Identity(4)
    for axis, angle in zip("XYZ", rotation):
        if angle:
            rot = Matrix.Rotation(math.radians(angle), 4, axis) @ rot
    return Matrix.Translation(Vector(location)) @ rot


def box_project_uvs(bm, scale):
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        n = face.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in face.loops:
            co = loop.vert.co
            if ax == 0:
                u, v = co.y, co.z
            elif ax == 1:
                u, v = co.x, co.z
            else:
                u, v = co.x, co.y
            loop[uv_layer].uv = (u / scale, v / scale)


# --------------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------------

def export_w3d(path):
    bpy.ops.export_mesh.westwood_w3d(filepath=path, file_format="W3D", export_mode="HM")


def render_preview(path, target=(0, 0, 10), distance=170.0, elevation=32.0, azimuth=-40.0, samples=48):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.device = "CPU"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = path

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.6, 0.68, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scene.world = world

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 4.0
    sun_data.angle = math.radians(3.0)
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.collection.objects.link(sun)

    ground_mesh = bpy.data.meshes.new("Ground")
    ground_bm = bmesh.new()
    bmesh.ops.create_grid(ground_bm, x_segments=1, y_segments=1, size=400)
    ground_bm.to_mesh(ground_mesh)
    ground = bpy.data.objects.new("Ground", ground_mesh)
    ground_mat = bpy.data.materials.new("GroundMat")
    ground_mat.use_nodes = True
    ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.32, 0.29, 0.22, 1.0)
    ground_mesh.materials.append(ground_mat)
    scene.collection.objects.link(ground)

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 50
    cam = bpy.data.objects.new("Camera", cam_data)
    el, az = math.radians(elevation), math.radians(azimuth)
    cam.location = (target[0] + distance * math.cos(el) * math.sin(az),
                    target[1] - distance * math.cos(el) * math.cos(az),
                    target[2] + distance * math.sin(el))
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    scene.camera = cam

    bpy.ops.render.render(write_still=True)
    for obj in (sun, ground, cam):
        bpy.data.objects.remove(obj)
