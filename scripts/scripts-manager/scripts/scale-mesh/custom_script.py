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
import math

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

        objs = self.common.getSelection(False)

        objs = [obj for obj in objs if obj.TypeId.startswith("Mesh::")]

        if len(objs) == 0:
            self.parent.statusMessage("No mesh selected.")
            return

        text, status = self.parent.inputDialog(
            self.modulePath, "Please enter the scales in \"scale-x,scale-y,scale-z\" format.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            scales = list(map(float, text.split(",")))
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        if (len(scales) != 3) or (0 in scales) or (math.inf in scales) or (-math.inf in scales):
            self.parent.statusMessage("Invalid input.")
            return

        matrix = FreeCAD.Matrix()
        matrix.scale(scales[0], scales[1], scales[2])

        FreeCAD.ActiveDocument.openTransaction()

        for obj in objs:
            meshCopy = obj.Mesh.copy()
            meshCopy.transformGeometry(matrix)
            obj.Mesh = meshCopy

        FreeCAD.ActiveDocument.commitTransaction()

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Scale selected mesh objects.\n"
                    "Supports unequal scaling across the three axes.\n"
                    "To mirror across an axis, use a negative value.")

        return aboutStr
# ==============================================================================
