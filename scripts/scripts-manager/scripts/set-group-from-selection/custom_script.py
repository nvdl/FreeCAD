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

        groups = [selObj for selObj in selObjs if type(selObj) is FreeCAD.DocumentObjectGroup]

        if len(groups) == 0:
            self.parent.statusMessage("No group selected.")
            return

        elif len(groups) > 1:
            self.parent.statusMessage("More than one groups selected.")
            return

        else:
            group = groups[0]

        selObjs = [selObj for selObj in selObjs if selObj is not group]

        if len(selObjs) == 0:
            self.parent.statusMessage("No object selected.")
            return

        for selObj in selObjs:
            group.addObject(selObj)

        self.parent.statusMessage(f"Done \"{self.modulePath}\"")
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Move objects to a group using the selection.\n"
                    "Select objects and a group to move the objects into the group.")

        return aboutStr
# ==============================================================================
