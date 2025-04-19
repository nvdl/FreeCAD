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
import re

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

        regexLabel, status = self.parent.inputDialog(
            self.modulePath, "Please enter the regex for labels (enter nothing to skip filtering).")

        if not status:
            self.parent.statusMessage("Cancelled.")
            return

        if regexLabel == "":
            regexLabel = ".*"

        regexTypeId, status = self.parent.inputDialog(
            self.modulePath, "Please enter the regex for type IDs (enter nothing to skip filtering).")

        if not status:
            self.parent.statusMessage("Cancelled.")
            return

        if regexTypeId == "":
            regexTypeId = ".*"

        FreeCADGui.Selection.clearSelection()

        foundCount = 0

        for obj in self.common.getAllObjects():
            if re.search(regexLabel, obj.Label) is None:
                continue

            if re.search(regexTypeId, obj.TypeId) is None:
                continue

            FreeCADGui.Selection.addSelection(obj)
            foundCount += 1

        self.parent.statusMessage(f"Found {foundCount} objects.")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Select objects based on their labels and/or type IDs."

        return aboutStr
# ==============================================================================
