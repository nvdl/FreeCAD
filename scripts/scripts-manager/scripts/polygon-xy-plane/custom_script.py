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
import re

import FreeCAD
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        text, status = self.parent.inputDialog(
            self.modulePath, "Please enter the vertices in \"(x1,y1)(x2,y2)(xn,yn)\" format.")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*\)"
        matches = re.findall(pattern=pattern, string=text)

        if len(matches) < 2:
            self.parent.messageBoxCritical(self.modulePath, "No enough vertices specified in the input string.")
            return

        polygonVertices = []

        for match in matches:
            x = int(match[0])
            y = int(match[1])
            polygonVertices.append(FreeCAD.Vector(x, y, 0))

        activeDocument = FreeCAD.activeDocument()

        polygon = activeDocument.addObject("Part::Polygon", self.modulePath.replace(".", "_"))
        polygon.Nodes = polygonVertices

        closePolygon = False

        if len(matches) > 2:
            if self.parent.messageBoxYesNo(self.modulePath, "Close the polygon?"):
                closePolygon = True

        polygon.Close = closePolygon

        activeDocument.recompute()
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Add a polygon in XY plane.\n"
                    "Input format is \"(x1,y1)(x2,y2)(xn,yn)\".")

        return aboutStr
# ==============================================================================
