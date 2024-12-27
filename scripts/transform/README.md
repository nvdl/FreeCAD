# About
This macro allows for positioning of a selection of objects.
It adds temporary bounding boxes and center marks before moving
the objects and removes them after the translation is complete.

It supports:
- Translation of a single, multiple or a group (FreeCAD group)
  of objects.
- Snapping to center and origin marks (after adding them).
- Addition of "edge-to-edge", "vertex-to-vertex" and
  "vertex-to-edge" dimensions.

# Screenshots
![screenshot-1](doc/images/screenshot-1.png?raw=true "Screenshot 1")
![screenshot-2](doc/images/screenshot-2.png?raw=true "Screenshot 2")

# Installation
Please refer to the official guide for installation of the macro:

https://wiki.freecad.org/How_to_install_macros

# Alternative Installation
A link to the script in the home directory of FreeCAD also works.
The Git repository can be checked out at a different location.

```
cd ~/.FreeCAD
ln -s path/to/git/repository/scripts/transform.py
```
