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
            self.parent.statusMessage("Please select an edge or a face.")
            return

        for selObj in selObjs:
            if len(selObj.SubObjects) == 0:
                self.parent.statusMessage("Selection is not supported.")
                continue

            self.parent.statusMessage(f"{selObj.SubObjects}")

            for name, subObject in zip(
                selObj.SubElementNames,
                selObj.SubObjects,
            ):
                if type(subObject) is Part.Vertex:
                    message = "Type: Vertex\n"
                    message += f"Name: {name}\n"
                    message += f"Position: ({subObject.X}, {subObject.Y}, {subObject.Z})"

                elif type(subObject) is Part.Edge:
                    message = "Type: Edge\n"
                    message += f"Name: {name}\n"
                    message += f"Length: {subObject.Length}\n\n"

                    vertices = subObject.Vertexes

                    for i, vertex in enumerate(vertices):
                        message += f"Vertex {i + 1} position: ({vertex.X}, {vertex.Y}, {vertex.Z})\n"

                elif type(subObject) is Part.Face:
                    message = "Type: Face\n"
                    message += f"Name: {name}\n"
                    message += f"Parameter length: {subObject.Length}\n"
                    message += f"Area: {subObject.Area}\n\n"

                    edges = subObject.Edges

                    for i, edge in enumerate(edges):
                        message += f"Edge {i + 1} length: {edge.Length}\n"

                else:
                    assert False

                self.parent.consoleMessage(message)
                self.parent.messageBoxInformation(self.modulePath, message)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Get information about selected vertices, edges or faces."

        return aboutStr
# ==============================================================================
