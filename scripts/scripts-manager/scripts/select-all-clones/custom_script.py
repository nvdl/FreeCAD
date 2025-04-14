'''
***************************************************************************
*                                                                         *
*   Author:  Naveed Alam                                                  *
*   Email:   naveedguy ayt gmail dot com                                  *
*   Source:  https://github.com/nvdl/FreeCAD                              *
*   License: https://github.com/FreeCAD/FreeCAD/blob/main/LICENSE         *
*                                                                         *
***************************************************************************
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                  *
*   See the GNU Library General Public License for more details.          *
*                                                                         *
***************************************************************************
'''
import FreeCADGui
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
        self.common = self.parent.getModule(modulePath="common", name="common", relative=False)
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        objs = self.common.getSelection(False)

        if len(objs) == 0:
            self.parent.statusMessage("Nothing selected.")
            return

        if len(objs) > 1:
            self.parent.statusMessage("Please select only one object.")
            return

        parentObj = objs[0]

        clones = []

        for obj in self.common.getAllObjects():
            if hasattr(obj, "Objects") and (len(obj.Objects) == 1) and (obj.Objects[0].Name == parentObj.Name):
                clones.append(obj)

        if clones:
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(parentObj)

            for clone in clones:
                FreeCADGui.Selection.addSelection(clone)

            self.parent.statusMessage(f"Found {len(clones)} clone(s).")
        else:
            self.parent.statusMessage("Found no clone(s).")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Find all clones of an object and select them.\n"
                    "The parent object also remains selected.")

        return aboutStr
# ==============================================================================
