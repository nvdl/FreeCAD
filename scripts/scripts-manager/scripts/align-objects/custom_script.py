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
import FreeCAD
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
        self.common = self.parent.getModule(modulePath="common", name="common", relative=False)
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        selObjs = self.common.getSelection(extended=False)

        if len(selObjs) < 2:
            self.parent.statusMessage("Please select at least two objects.")
            return

        try:
            axisType = self.parent.optionsDialogExc("single", "Axis to align along:", ["x", "y", "z"])[0]
        except ValueError:
            self.parent.statusMessage("Canceled or wrong input.")
            return

        FreeCAD.ActiveDocument.openTransaction()

        centerParent = selObjs[0].Placement.Base

        for obj in selObjs[1:]:
            center = obj.Placement.Base

            dx = centerParent[0] - center[0]
            dy = centerParent[1] - center[1]
            dz = centerParent[2] - center[2]

            if axisType == "x":
                newBase = FreeCAD.Vector(center[0] + dx, center[1], center[2])
            elif axisType == "y":
                newBase = FreeCAD.Vector(center[0], center[1] + dy, center[2])
            elif axisType == "z":
                newBase = FreeCAD.Vector(center[0], center[1], center[2] + dz)

            obj.Placement.Base = newBase

        FreeCAD.ActiveDocument.commitTransaction()

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Align objects.\n"
                    "All objects are aligned to the first object in a selection.\n"
                    "Does not support rotated objects.\n"
                    "To get the expected result, the rotation transform shall be applied so that the base rotation "
                    "represents no rotation.")

        return aboutStr
# ==============================================================================
