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
import Draft
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

        text, status = self.parent.inputDialog(
            self.modulePath, "Please enter the scales in \"scale-x,scale-y,scale-z\" format or only one number for uniform scaling.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            scales = list(map(float, text.split(",")))
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        if len(scales) not in [1, 3]:
            self.parent.statusMessage("Invalid input.")
            return

        if (0 in scales) or (math.inf in scales) or (-math.inf in scales):
            self.parent.statusMessage("Invalid input.")
            return

        text, status = self.parent.inputDialog(
            self.modulePath, "Please enter the number of clones.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            numClones = int(text)
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        if numClones <= 0:
            self.parent.statusMessage("Invalid input.")
            return

        if len(scales) == 3:
            vecScale = FreeCAD.Vector(scales[0], scales[1], scales[2])
        else:
            vecScale = FreeCAD.Vector(scales[0], scales[0], scales[0])

        for obj in objs:
            for _ in range(numClones):
                clone = Draft.make_clone(obj)
                clone.Scale = vecScale
                clone.Label = f"clone-{obj.Label}"

        FreeCAD.ActiveDocument.recompute()

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Clone and scale objects.\n"
                    "The clones are automatically updated when the original object is updated.")

        return aboutStr
# ==============================================================================
