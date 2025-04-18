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
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\"")

        selObjs = self.common.getSelection(extended=False)

        if len(selObjs) == 0:
            self.parent.statusMessage("Nothing selected.")
            return

        unions = [obj for obj in selObjs if obj.TypeId == "Part::MultiFuse"]

        if len(unions) == 0:
            self.parent.statusMessage("No union selected.")
            return

        elif len(unions) > 1:
            self.parent.statusMessage("More than one unions selected.")
            return

        else:
            union = unions[0]

        selObjs = [obj for obj in selObjs if obj is not union]

        if len(selObjs) == 0:
            self.parent.statusMessage("No object selected.")
            return

        FreeCAD.ActiveDocument.openTransaction()

        union.Shapes = union.Shapes + selObjs

        FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()

        self.parent.statusMessage(f"Done \"{self.modulePath}\"")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Add selected objects to a union.\n"
                    "Select objects and a union to move the objects into the union.")

        return aboutStr
# ==============================================================================
