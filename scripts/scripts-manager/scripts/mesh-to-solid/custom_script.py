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

        objs = self.common.getSelection(False)

        objs = [obj for obj in objs if obj.TypeId.startswith("Mesh::")]

        if len(objs) == 0:
            self.parent.statusMessage("No mesh selected.")
            return

        text, status = self.parent.inputDialog(self.modulePath,
                                               "Please enter tolerance for sewing the shape (default: 0.1).")

        if not status or text == "":
            self.parent.statusMessage("Cancelled or empty input.")
            return

        try:
            tolerance = float(text)
        except ValueError:
            self.parent.statusMessage("Invalid input.")
            return

        for obj in objs:
            # --s Get shape from the mesh.
            newObj = FreeCAD.ActiveDocument.addObject("Part::Feature", "tmp_part_" + obj.Name)

            shape = Part.Shape()
            shape.makeShapeFromMesh(obj.Mesh.Topology, tolerance, True)

            newObj.Shape = shape
            newObj.purgeTouched()

            del shape
            FreeCAD.ActiveDocument.recompute()
            # --e Get shape from the mesh.

            # --s Get solid from the shape.
            shape = Part.Solid(newObj.Shape)

            newObj2 = FreeCAD.ActiveDocument.addObject("Part::Feature", "tmp_solid_" + obj.Name)
            newObj2.Label = "Component023 (Solid)"
            newObj2.Shape = shape

            del shape
            FreeCAD.ActiveDocument.recompute()
            # --e Get solid from the shape.

            # --s Refine the solid.
            newObj3 = FreeCAD.ActiveDocument.addObject("Part::Refine", "tmp_refined_" + obj.Name)
            newObj3.Source = newObj2

            FreeCAD.ActiveDocument.recompute()
            # --e Refine the solid.

            # --s Create a simple copy to remove dependency.
            # shape = Part.getShape(newObj3, "", needSubElement=False, refine=False)
            shape = Part.getShape(newObj3, "", needSubElement=False, refine=True)

            newObj4 = FreeCAD.ActiveDocument.addObject("Part::Feature", "solid_" + obj.Name)

            newObj4.Shape = shape
            newObj4.Label = "solid-" + obj.Label

            # newObj4.ViewObject.LineColor = obj.ViewObject.LineColor
            # newObj4.ViewObject.LineWidth = obj.ViewObject.LineWidth
            # newObj4.ViewObject.PointColor = obj.ViewObject.LineColor
            # newObj4.ViewObject.PointSize = obj.ViewObject.PointSize
            # newObj4.ViewObject.ShapeAppearance = obj.ViewObject.ShapeAppearance
            # newObj4.ViewObject.Transparency = obj.ViewObject.Transparency

            FreeCAD.ActiveDocument.recompute()
            # --e Create a simple copy to remove dependency.

            for toRemove in [newObj, newObj2, newObj3]:
                FreeCAD.ActiveDocument.removeObject(toRemove.Name)

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Create refined solids from meshes."

        return aboutStr
# ==============================================================================
