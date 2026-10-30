# Art pipeline

Models are built with Blender 4.2 and the OpenSAGE W3D plugin, run headless:

    blender -b --factory-startup --python <script.py> -- <args>

Blender lives in `%LOCALAPPDATA%\Programs\blender-4.2.23-windows-x64` and the plugin in
`%LOCALAPPDATA%\Programs\OpenSAGE.BlenderPlugin` (cloned with `--recurse-submodules`).

`bigextract.py <archive.big> <outdir> <substring>` pulls files out of the retail archives.
Base Generals assets that Zero Hour still uses are in `ZH_Generals\*.big`.

`w3d_inspect.py -- <file.w3d>` prints the hierarchy, meshes and textures of a model.

Models derived from retail art are written to `Operational/ArtLocal`, which is not committed.
Original models go to `Operational/Art`. The deploy script copies both into the game folder.
