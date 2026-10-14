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
            self.parent.statusMessage("Please select a vertex, an edge or a face.")
            return

        for selObj in selObjs:
            if len(selObj.SubObjects) == 0:
                self.parent.statusMessage("Selection is not supported.")
                continue

            self.parent.statusMessage(f"{selObj.SubObjects}")

            obj = selObj.Object

            message = f"Name: {obj.Name}\n"
            message += f"Label: {obj.Label}\n\n"

            vertices = []
            edges = []
            faces = []

            import re

            for name in selObj.SubElementNames:
                match = re.search(r"\d+$", name)

                if not match:
                    continue

                index = int(match[0])

                if name.startswith("Vertex"):
                    vertices.append(index)
                elif name.startswith("Edge"):
                    edges.append(index)
                elif name.startswith("Face"):
                    faces.append(index)

                message += f"{name}\n"

            vertices.sort()
            edges.sort()
            faces.sort()

            if vertices:
                message += f"\nvertices = {tuple(vertices)}"

            if edges:
                message += f"\nedges = {tuple(edges)}"

            if faces:
                message += f"\nfaces = {tuple(faces)}"

            self.parent.consoleMessage(message)
            self.parent.messageBoxInformation(self.modulePath, message)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Get names of selected vertices, edges or faces."

        return aboutStr
# ==============================================================================
