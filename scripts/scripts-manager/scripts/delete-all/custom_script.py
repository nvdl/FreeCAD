'''
***************************************************************************
*                                                                         *
*   Author:  Naveed Alam.                                                 *
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

        self.parent.statusMessage(f"Running \"{self.modulePath}\"")

        ret = self.parent.messageBoxYesNo(
            self.modulePath, "This will delete the selected object and all of its sub objects. Continue?")

        if ret:
            FreeCADGui.activateWorkbench("OpenSCADWorkbench")
            FreeCADGui.runCommand("OpenSCAD_RemoveSubtree", 0)

            # TODO: Revert to the correct workbench.
            FreeCADGui.activateWorkbench("PartWorkbench")
        else:
            self.parent.statusMessage("Canceled.")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Uses \"OpenSCAD_RemoveSubtree\" to delete an object and all of its subobjects."

        return aboutStr
# ==============================================================================
