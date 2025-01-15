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

        label = self.parent.getScriptData(key="selectionLabel")

        if label is None:
            self.parent.statusMessage("No data found.")

            self.parent.messageBoxInformation(self.modulePath,
                                              ("No data found.\n"
                                               "Please use the selection script to choose the label of the target group."))

            return

        groups = FreeCAD.ActiveDocument.getObjectsByLabel(label)

        if len(groups) == 0:
            self.parent.statusMessage("No group found.")
            return

        group = groups[0]

        if type(group) != FreeCAD.DocumentObjectGroup:
            self.parent.statusMessage("Selection is not a group of objects.")

            self.parent.messageBoxInformation(self.modulePath,
                                              ("Selection is not a group of objects.\n"
                                               "Please use the selection script to choose the label of the target group."))

            return

        for selObj in selObjs:
            group.addObject(selObj)
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Move objects to a group using the saved label.\n"
                    "Use the selection script to choose/save the label of the target group.")

        return aboutStr
# ==============================================================================
