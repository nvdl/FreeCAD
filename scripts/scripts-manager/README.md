# About
This macro acts as a scripts' manager.
Scripts should be placed in a directory named "scripts".
This script and the "scripts" directory should be in the same parent directory.
Each custom script needs its own directory containing the main script named "custom_script.py".

The main script, "custom_script.py", should contain a class as below:

```
class CustomScript():
    def __init__(self, parent, modulePath) -> None:
        self.parent = parent
        self.modulePath = modulePath
    def run(self) -> None:
        // Code to run.
    def about(self) -> str:
        // Helpful information about the script.
```

# Screenshots
![screenshot-1](doc/images/screenshot-1.png?raw=true "Screenshot 1")

# Tips
To move objects to a group, select the group and use "select-label" script to save the group's label.
Next, select the objects and run "set-group-from-label-selection" to move the objects to the previously specified group.

To apply an object's placement (translation and rotation) on other objects, select the source object and run
"select-position". Next, select the target objects and run "set-position-from-position-selection".
It is helpful when importing an updated version of a model that has to be placed exactly at its spot.

# Installation
Please refer to the official guide for installation of the macro:

https://wiki.freecad.org/How_to_install_macros

# Alternative Installation
A link to the script in the home directory of FreeCAD also works.
The Git repository can be checked out at a different location.

```
cd ~/.FreeCAD
ln -s path/to/git/repository/scripts/scripts-manager.py
```
