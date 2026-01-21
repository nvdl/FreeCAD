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

        self.GROUP_LABEL_GRID_LINES = "lines_grid"
# ==============================================================================
    def addLine(self,
                planeType,
                planeSize,
                planePos,
                planeOffset,
                lineColor,
                lineWidth,
                lineTransparency):

        for axisType in planeType:
            strPlaneOffset = str(planeOffset).replace("-", "m").replace(".", "p")
            strPlanePos = str(planePos).replace("-", "m").replace(".", "p")

            objNameLabel = f"line_grid_{axisType}_{planeType}_off_{strPlaneOffset}_pos_{strPlanePos}"

            line = FreeCAD.ActiveDocument.addObject("Part::Line", objNameLabel)
            line.Label = objNameLabel

            if planeType == "xy":
                line.Z1 = line.Z2 = planeOffset
                if axisType == "x":
                    line.X1 = -planeSize
                    line.X2 = planeSize
                    line.Y1 = line.Y2 = planePos
                elif axisType == "y":
                    line.Y1 = -planeSize
                    line.Y2 = planeSize
                    line.X1 = line.X2 = planePos

            elif planeType == "xz":
                line.Y1 = line.Y2 = planeOffset
                if axisType == "x":
                    line.X1 = -planeSize
                    line.X2 = planeSize
                    line.Z1 = line.Z2 = planePos
                elif axisType == "z":
                    line.Z1 = -planeSize
                    line.Z2 = planeSize
                    line.X1 = line.X2 = planePos

            elif planeType == "yz":
                line.X1 = line.X2 = planeOffset
                if axisType == "y":
                    line.Y1 = -planeSize
                    line.Y2 = planeSize
                    line.Z1 = line.Z2 = planePos
                elif axisType == "z":
                    line.Z1 = -planeSize
                    line.Z2 = planeSize
                    line.Y1 = line.Y2 = planePos

            line.ViewObject.Selectable = False
            line.ViewObject.LineColor = lineColor
            line.ViewObject.LineWidth = lineWidth
            line.ViewObject.Transparency = lineTransparency

            self.common.addToGroup((line,), self.GROUP_LABEL_GRID_LINES)
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        try:
            planeType = self.parent.optionsDialogExc("single", "Type of the plane:", ["xy", "xz", "yz"])[0]

            planeSize = float(self.parent.inputDialogExc(self.modulePath,
                                                         "Size of the plane:",
                                                         "100"))

            lineSpacing = float(self.parent.inputDialogExc(self.modulePath,
                                                           "Spacing between lines:",
                                                           "5"))

            lineColor = self.parent.colorDialogExc(self.modulePath,
                                                   initialColor=(0.4, 0.4, 0.4))

            lineTransparency = int(self.parent.inputDialogExc(
                self.modulePath,
                "Transparency of lines (0 to 100):",
                "50"))

            lineWidth = float(self.parent.inputDialogExc(self.modulePath,
                                                         "Thickness of lines:",
                                                         "1"))

            planeOffset = float(self.parent.inputDialogExc(self.modulePath,
                                                           "Offset of the plane:",
                                                           "0"))

            linesOrigin = self.parent.messageBoxYesNo(self.modulePath, "Draw lines at the origin?")

        except ValueError:
            self.parent.statusMessage("Canceled or wrong input.")
            return

        lines = int(planeSize / lineSpacing)

        for i in range(-lines, lines + 1):
            if (i == 0) and (not linesOrigin):
                continue

            planePos = i * lineSpacing

            self.addLine(planeType,
                         planeSize,
                         planePos,
                         planeOffset,
                         lineColor,
                         lineWidth,
                         lineTransparency)

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Add 2D grids to the GUI."

        return aboutStr
# ==============================================================================
