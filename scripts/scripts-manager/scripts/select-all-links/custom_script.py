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
import FreeCADGui
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
        self.common = self.parent.getModule(modulePath="common", name="common", relative=False)
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        selObjs = self.common.getSelection(False)

        if len(selObjs) == 0:
            self.parent.statusMessage("Nothing selected.")
            return

        if len(selObjs) > 1:
            self.parent.statusMessage("Please select only one object.")
            return

        parentObj = selObjs[0]

        links = [obj for obj in self.common.getAllObjects() if (obj.TypeId == "App::Link")
                 and (obj.LinkedObject is parentObj)]

        if links:
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(parentObj)

            for link in links:
                FreeCADGui.Selection.addSelection(link)

            self.parent.statusMessage(f"Found {len(links)} link(s).")
        else:
            self.parent.statusMessage("Found no link(s).")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Find all links of an object and select them.\n"
                    "The parent object also remains selected.")

        return aboutStr
# ==============================================================================
