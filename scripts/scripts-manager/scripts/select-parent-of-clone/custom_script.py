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

        selObjs = self.common.getSelection(False)

        selObjs = [obj for obj in selObjs if (obj.TypeId == "Part::FeaturePython") and hasattr(obj, "Objects")]

        if len(selObjs) == 0:
            self.parent.statusMessage("No clone selected.")
            return

        if len(selObjs) > 1:
            self.parent.statusMessage("Please select only one object.")
            return

        selObj = selObjs[0]

        if len(selObj.Objects) == 0:
            self.parent.statusMessage("Clone has no parent.")
            return

        if len(selObj.Objects) != 1:
            self.parent.statusMessage("Clone has more than one parents.")
            return

        parentName = selObj.Objects[0].Name

        for obj in self.common.getAllObjects():
            if obj.Name == parentName:
                FreeCADGui.Selection.clearSelection()
                FreeCADGui.Selection.addSelection(selObj)
                FreeCADGui.Selection.addSelection(obj)
                self.parent.statusMessage(f"Found \"{obj.Label}\" as the parent.")
                break
        else:
            self.parent.statusMessage("Found no parent.")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Find parent of the clone and select it.\n"
                    "The cloned object also remains selected.")

        return aboutStr
# ==============================================================================
