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

            for selObj2 in selObj.SubObjects:
                if type(selObj2) is Part.Vertex:
                    message = "Type: vertex\n\n"
                    message += f"Position: ({selObj2.X}, {selObj2.Y}, {selObj2.Z})"

                elif type(selObj2) is Part.Edge:
                    message = "Type: edge\n\n"
                    message += "Edge "
                    message += f"length: {selObj2.Length}\n\n"

                    vertices = selObj2.Vertexes

                    for i, vertex in enumerate(vertices):
                        message += f"Vertex {i + 1} position: ({vertex.X}, {vertex.Y}, {vertex.Z})\n"

                elif type(selObj2) is Part.Face:
                    message = "Type: face\n\n"
                    message += "Parameter "
                    message += f"length: {selObj2.Length}\n\n"

                    edges = selObj2.Edges

                    for i, edge in enumerate(edges):
                        message += f"Edge {i + 1} length: {edge.Length}\n"

                    message += f"\nArea: {selObj2.Area}"

                else:
                    assert False

                self.parent.consoleMessage(message)
                self.parent.messageBoxInformation(self.modulePath, message)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Get information about selected vertices, edges or faces."

        return aboutStr
# ==============================================================================
