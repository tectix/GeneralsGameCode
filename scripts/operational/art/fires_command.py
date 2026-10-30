"""Original model for the Fires Command structure.

Usage: blender -b --factory-startup --python fires_command.py -- <out_dir> [preview.png]
Writes Art/W3D/TCFiresCmd.w3d and its textures to Art/Textures under out_dir.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))
import modelkit as mk  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out_dir = args[0]
preview = args[1] if len(args) > 1 else None
w3d_dir = os.path.join(out_dir, "Art", "W3D")
tex_dir = os.path.join(out_dir, "Art", "Textures")
os.makedirs(w3d_dir, exist_ok=True)
os.makedirs(tex_dir, exist_ok=True)

mk.start_scene()

concrete = mk.make_material("concrete", mk.make_texture("tcfc_concrete", tex_dir, (0.56, 0.55, 0.51), seed=3, grime=0.45, panel_lines=3, line_darkness=0.18, streaks=0.3))
bunker = mk.make_material("bunker", mk.make_texture("tcfc_bunker", tex_dir, (0.37, 0.39, 0.30), seed=5, grime=0.5, streaks=0.35))
steel = mk.make_material("steel", mk.make_texture("tcfc_steel", tex_dir, (0.34, 0.36, 0.31), seed=8, grime=0.3, panel_lines=4, line_darkness=0.22))
dark = mk.make_material("darksteel", mk.make_texture("tcfc_darksteel", tex_dir, (0.17, 0.18, 0.17), seed=11, grime=0.25, panel_lines=3, line_darkness=0.3))
glass = mk.make_material("glass", mk.make_texture("tcfc_glass", tex_dir, (0.07, 0.11, 0.14), seed=13, grime=0.15, speckle=0.02), emissive=(0.02, 0.05, 0.06))
canister = mk.make_material("canister", mk.make_texture("tcfc_canister", tex_dir, (0.56, 0.51, 0.39), seed=17, grime=0.35, panel_lines=2, line_darkness=0.25, streaks=0.2))
team = mk.make_material("team", mk.make_texture("tcfc_team", tex_dir, (0.92, 0.92, 0.92), seed=19, grime=0.15, speckle=0.03))

body = mk.Builder("BODY")

# Concrete pad and kerb.
body.box(concrete, (104, 116, 1.2), (0, 0, 0.6), bevel=0.3)
body.box(concrete, (100, 112, 0.6), (0, 0, 1.4), bevel=0.2)

# Hardened bunker: sloped, earth-covered walls.
bx, by = -8.0, 4.0
body.hull(bunker, [(-32, -28, 1.7), (32, -28, 1.7), (32, 28, 1.7), (-32, 28, 1.7),
                   (-25, -21, 15), (25, -21, 15), (25, 21, 15), (-25, 21, 15)], (bx, by, 0))
body.box(steel, (51, 43, 0.8), (bx, by, 15.4), bevel=0.2)

# Vehicle bay on the exit side (+X), with a segmented blast door.
body.box(steel, (18, 24, 12), (bx + 33, by - 8, 7.7), bevel=0.4)
body.box(dark, (0.8, 18, 9), (bx + 42.3, by - 8, 6.2))
for k in range(4):
    body.box(steel, (1.0, 18.4, 0.5), (bx + 42.6, by - 8, 2.4 + k * 2.4))
body.box(steel, (6, 28, 1.0), (bx + 39.5, by - 8, 14.2), bevel=0.2)

# Command tower with an observation glass band.
tx, ty = bx - 12, by - 6
body.box(steel, (16, 16, 13), (tx, ty, 22.3), bevel=0.3)
body.box(glass, (16.6, 16.6, 3.2), (tx, ty, 25.5))
body.box(dark, (18, 18, 1.0), (tx, ty, 29.3), bevel=0.2)
for sx, sy in ((5, 5), (-5, 5), (5, -5)):
    body.box(steel, (3, 3, 1.6), (tx + sx, ty + sy, 30.6), bevel=0.15)

# Radar mast on the tower.
body.cylinder(dark, 1.0, 12, (tx, ty, 36), segments=12)
body.cylinder(steel, 2.2, 1.2, (tx, ty, 42), segments=16)

# Antenna farm on the bunker roof.
for i, (ax, ay, h) in enumerate(((12, 14, 18), (16, 10, 14), (9, 8, 20), (18, 17, 12))):
    body.cylinder(dark, 0.3, h, (bx + ax, by + ay, 15.8 + h / 2), segments=8)
    body.box(steel, (1.6, 1.6, 1.2), (bx + ax, by + ay, 15.8 + h * 0.7))
    body.cylinder(steel, 1.0, 0.6, (bx + ax, by + ay, 16.1), segments=10)

# Satellite comms dishes.
for dx in (6, 15):
    body.cylinder(dark, 0.7, 3.5, (bx + dx, by - 14, 17.5), segments=10)
    body.dish(steel, 3.2, 1.2, (bx + dx, by - 14, 20.0), rotation=(-55, 0, 25))

# Missile canister rack on the south side of the pad.
rx, ry = -6.0, -44.0
body.box(dark, (34, 10, 1.2), (rx, ry, 2.6), bevel=0.2)
for px in (-14, 0, 14):
    body.box(dark, (1.4, 1.4, 7), (rx + px, ry + 3.5, 5.6))
    body.box(dark, (1.4, 1.4, 3), (rx + px, ry - 3.5, 3.6))
for k, cy in enumerate((-3.0, 1.6)):
    for row, cz in enumerate((6.5, 11.0)):
        body.box(canister, (30, 4.2, 4.2), (rx, ry + cy, cz), rotation=(0, -12, 0), bevel=0.25)
        body.box(dark, (0.6, 4.4, 4.4), (rx + 15.0, ry + cy, cz + 3.2), rotation=(0, -12, 0))

# Blast walls around the north and west edges.
for i in range(9):
    body.hull(concrete, [(-2, -0.9, 0), (2, -0.9, 0), (2, 0.9, 0), (-2, 0.9, 0),
                         (-2, -0.4, 4.5), (2, -0.4, 4.5), (2, 0.4, 4.5), (-2, 0.4, 4.5)],
              (-40 + i * 5.2, 54, 1.7))
for i in range(8):
    body.hull(concrete, [(-0.9, -2, 0), (0.9, -2, 0), (0.9, 2, 0), (-0.9, 2, 0),
                         (-0.4, -2, 4.5), (0.4, -2, 4.5), (0.4, 2, 4.5), (-0.4, 2, 4.5)],
              (-48, 34 - i * 5.2, 1.7))

# Generator and fuel tanks behind the bunker.
body.box(steel, (10, 6, 5), (-38, -20, 4.2), bevel=0.3)
for k in range(2):
    body.cylinder(canister, 2.4, 9, (-38, -32 + k * 5.5, 4.0), rotation=(0, 90, 0), segments=16)

body_obj = body.build()

# Team color trim: roof edge bands and a band around the tower.
trim = mk.Builder("HOUSECOLOR01")
trim.box(team, (51.6, 1.4, 0.7), (bx, by - 21.0, 15.9))
trim.box(team, (51.6, 1.4, 0.7), (bx, by + 21.0, 15.9))
trim.box(team, (16.8, 16.8, 1.1), (tx, ty, 19.0))
trim.box(team, (1.0, 6.0, 6.0), (bx + 42.9, by + 7.0, 8.0))
trim.build()

# Radar dish as its own sub-object so it can be animated later.
radar = mk.Builder("RADARDISH")
radar.dish(steel, 7.0, 2.6, (tx, ty + 1.5, 44.5), rotation=(-70, 0, 0), segments=28)
radar.box(dark, (0.8, 0.8, 4.0), (tx, ty + 3.2, 45.2), rotation=(-20, 0, 0))
radar.build()

mk.export_w3d(os.path.join(w3d_dir, "TCFiresCmd.w3d"))
print("EXPORTED TCFiresCmd")

if preview:
    mk.render_preview(preview, target=(-6, 0, 12), distance=190.0, elevation=30.0, azimuth=-35.0)
    print("PREVIEW", preview)
