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
from pathlib import Path

import FreeCAD
import FreeCADGui
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

        text, status = self.parent.inputDialog(self.modulePath, "Please enter the text height.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            textSize = float(text)
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        if textSize <= 0:
            self.parent.statusMessage("Invalid input.")
            return

        text, status = self.parent.inputDialog(self.modulePath, "Please enter the extrusion length.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            extrusionLength = float(text)
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        if extrusionLength <= 0:
            self.parent.statusMessage("Invalid input.")
            return

        text, status = self.parent.inputDialog(self.modulePath, "Please enter the path to a font file.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        fontPath = text

        if not Path(fontPath).is_file():
            self.parent.statusMessage("Invalid path.")
            return

        text, status = self.parent.inputDialog(self.modulePath, "Please enter the text.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        FreeCAD.ActiveDocument.openTransaction()

        txt = Draft.makeShapeString(text, fontPath, Size=textSize, Tracking=0)

        # Limit length of the label.
        txt.Label = text[:20]

        txtExtruded = Draft.extrude(txt, FreeCAD.Vector(0, 0, extrusionLength))
        txtExtruded.Label = f"extruded-{text[:20]}"

        FreeCAD.ActiveDocument.commitTransaction()

        FreeCAD.ActiveDocument.recompute()

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Add extruded text."

        return aboutStr
# ==============================================================================
