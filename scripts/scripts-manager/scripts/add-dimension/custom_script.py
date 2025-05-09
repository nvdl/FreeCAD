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
import FreeCADGui
import Draft
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

        selection = self.common.getSelection(extended=True)

        obj1 = obj2 = None

        if len(selection) == 1:
            subObjs = selection[0].SubObjects

            if len(subObjs) == 2:
                obj1 = subObjs[0]
                obj2 = subObjs[1]

        elif len(selection) == 2:
            subObjs1 = selection[0].SubObjects
            subObjs2 = selection[1].SubObjects

            if len(subObjs1) == 1 and len(subObjs2) == 1:
                obj1 = subObjs1[0]
                obj2 = subObjs2[0]

        if (obj1 is None) or (obj2 is None):
            self.parent.statusMessage("Please select two parts; edge or vertex.")
            return

        p1 = p2 = None

        if type(obj1) == Part.Vertex:
            p1 = FreeCAD.Vector(obj1.X, obj1.Y, obj1.Z)
        elif type(obj1) == Part.Edge:
            p1 = obj1.firstVertex().Point

        if type(obj2) == Part.Vertex:
            p2 = FreeCAD.Vector(obj2.X, obj2.Y, obj2.Z)
        elif type(obj2) == Part.Edge:
            p2 = obj2.firstVertex().Point

        if (p1 is None) or (p2 is None):
            self.parent.statusMessage("Please select two parts; edge or vertex.")
            return

        selection, status = self.parent.optionsDialog("single", "Please select axis of the dimension.", ["X", "Y", "Z"])

        if not status:
            return

        dimensionType = selection[0]

        if dimensionType == "X":
            p2 = FreeCAD.Vector(p2.x, p1.y, p1.z)
        elif dimensionType == "Y":
            p2 = FreeCAD.Vector(p1.x, p2.y, p1.z)
        elif dimensionType == "Z":
            p2 = FreeCAD.Vector(p1.x, p1.y, p2.z)
        else:
            return

        if p1 == p2:
            self.parent.statusMessage("Cannot add a dimension of zero length.")
            return

        FreeCAD.ActiveDocument.openTransaction()

        dimension = Draft.make_dimension(p1, p2)

        dimensionView = dimension.ViewObject
        self.defaults(dimensionView)

        FreeCAD.ActiveDocument.commitTransaction()

        FreeCAD.ActiveDocument.recompute()

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    @staticmethod
    def defaults(dimensionView):
        """
        Default parameters to use for a new dimension.
        """

        dimensionView.FontName = "CommitMono"
        dimensionView.FontSize = 0.5
        dimensionView.TextColor = (0, 0, 0)
        dimensionView.TextSpacing = 0.1
        dimensionView.LineColor = (0, 0, 0)
        dimensionView.LineWidth = 3
        dimensionView.Decimals = 0
        dimensionView.ShowUnit = False
        dimensionView.ArrowType = "Arrow"
        dimensionView.ScaleMultiplier = 10
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Add a dimension by selecting two parts; edge or vertex.\n"
                    "Supports edge-to-edge, vertex-to-vertex and vertex-to-edge dimensions.\n"
                    "Please edit the script to set the default parameters for the dimension.")

        return aboutStr
# ==============================================================================
