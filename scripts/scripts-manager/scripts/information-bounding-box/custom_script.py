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

        selObjs = self.common.getSelection(extended=False)

        if len(selObjs) == 0:
            self.parent.statusMessage("No object selected.")
            return

        for obj in selObjs:
            if obj.TypeId.startswith("Part::") or obj.TypeId.startswith("App::"):
                boundingBox = obj.Shape.BoundBox

            elif obj.TypeId.startswith("Mesh::"):
                boundingBox = obj.Mesh.BoundBox

            else:
                self.parent.messageBoxWarning(self.modulePath,
                                              f"\"{obj.Label}\" with type ID \"{obj.TypeId}\" is not supported.")

                continue

            message = f"Label: {obj.Label}\n"
            message += f"Name: {obj.Name}\n"
            message += f"Type ID: {obj.TypeId}\n\n"

            message += f"X-Length: {boundingBox.XLength}\n"
            message += f"Y-Length: {boundingBox.YLength}\n"
            message += f"Z-Length: {boundingBox.ZLength}\n"
            message += f"Diagonal-Length: {boundingBox.DiagonalLength}\n\n"

            message += f"X-Center: {boundingBox.Center.x}\n"
            message += f"Y-Center: {boundingBox.Center.y}\n"
            message += f"Z-Center: {boundingBox.Center.z}\n\n"

            message += f"X-Min: {boundingBox.XMin}\n"
            message += f"X-Max: {boundingBox.XMax}\n"
            message += f"Y-Min: {boundingBox.YMin}\n"
            message += f"Y-Max: {boundingBox.YMax}\n"
            message += f"Z-Min: {boundingBox.ZMin}\n"
            message += f"Z-Max: {boundingBox.ZMax}\n"

            self.parent.messageBoxInformation(self.modulePath, message)

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Get information about the bounding box."

        return aboutStr
# ==============================================================================
