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

        if len(selObjs) != 2:
            self.parent.messageBoxInformation(self.modulePath, "Please select only two objects.")
            return

        base1 = selObjs[0].Placement.Base
        base2 = selObjs[1].Placement.Base

        dx = base1[0] - base2[0]
        dy = base1[1] - base2[1]
        dz = base1[2] - base2[2]

        diagXYZ = math.hypot(dx, dy, dz)
        diagXY = math.hypot(dx, dy)
        diagXZ = math.hypot(dx, dz)
        diagYZ = math.hypot(dy, dz)

        message = f"dX: {dx}\ndY: {dy}\ndZ:{dz}\n\n"

        message += f"XYZ-Diagonal-Length: {diagXYZ}\n"
        message += f"XY-Diagonal-Length: {diagXY}\n"
        message += f"XZ-Diagonal-Length: {diagXZ}\n"
        message += f"YZ-Diagonal-Length: {diagYZ}"

        self.parent.consoleMessage(message)
        self.parent.messageBoxInformation(self.modulePath, message)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Measure distances between bases of two objects."

        return aboutStr
# ==============================================================================
