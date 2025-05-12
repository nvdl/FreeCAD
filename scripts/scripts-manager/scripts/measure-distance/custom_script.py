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
import Part
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
        self.common = self.parent.getModule(modulePath="common", name="common", relative=False)
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        selObjs = self.common.getSelection(extended=True)

        if len(selObjs) == 0:
            self.parent.messageBoxInformation(self.modulePath, ("Please select two features.\n"
                                                                "A feature can be either a vertex or an edge."))

            return

        obj1 = obj2 = None

        if len(selObjs) == 1:
            subObjs = selObjs[0].SubObjects

            if len(subObjs) == 2:
                obj1 = subObjs[0]
                obj2 = subObjs[1]

        elif len(selObjs) == 2:
            subObjs1 = selObjs[0].SubObjects
            subObjs2 = selObjs[1].SubObjects

            if len(subObjs1) == 1 and len(subObjs2) == 1:
                obj1 = subObjs1[0]
                obj2 = subObjs2[0]

        if obj1 == None or obj2 == None:
            self.parent.statusMessage("Please select two features; vertex or edge.")
            return

        p1 = p2 = None

        if type(obj1) is Part.Vertex:
            p1 = FreeCAD.Vector(obj1.X, obj1.Y, obj1.Z)
        elif type(obj1) is Part.Edge:
            p1 = obj1.firstVertex().Point

        if type(obj2) is Part.Vertex:
            p2 = FreeCAD.Vector(obj2.X, obj2.Y, obj2.Z)
        elif type(obj2) is Part.Edge:
            p2 = obj2.firstVertex().Point

        if p1 == None or p2 == None:
            self.parent.statusMessage("Please select two features; vertex or edge.")
            return

        assert p1 is not None
        assert p2 is not None

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dz = p2.z - p1.z

        message = f"dX: {dx}\ndY: {dy}\ndZ:{dz}"

        self.parent.consoleMessage(message)
        self.parent.messageBoxInformation(self.modulePath, message)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Measure distances between vertices and edges."

        return aboutStr
# ==============================================================================
