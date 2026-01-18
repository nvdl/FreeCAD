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

from PySide import QtWidgets
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        activeDoc = FreeCADGui.activeDocument()

        if activeDoc is None:
            self.parent.statusMessage(f"\"{self.modulePath}\": No active document is available.")
            return

        activeView = activeDoc.activeView()

        if activeView is None:
            self.parent.statusMessage(f"\"{self.modulePath}\": No active view is available.")
            return

        # self.parent.messageBoxInformation("Active view", str(activeView))
        # return

        # filters = "PNG images (*.png);;JPG images (*.jpg)"
        filters = "PNG images (*.png)"
        fName, selectedFilter = self.parent.fileSaveDialog("Please specify the destination file.", filters)

        if fName == "":
            self.parent.statusMessage(f"\"{self.modulePath}\": Canceled.")
            return

        if not fName.endswith(".png"):
            fName = f"{fName}.png"

        # From the 3D view.
        if str(activeView) == "View3DInventor":
            backgroundColor = self.parent.optionsDialogExc("single",
                                                           "Background color:",
                                                           ["Transparent",
                                                            "Black",
                                                            "White",
                                                            "Current-Background"])[0]

            if backgroundColor == "Current-Background":
                viewParams = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
                # backgroundType = viewParams.GetInt("BackgroundType", 0)
                backgroundColorInt = viewParams.GetUnsigned("BackgroundColor", 0)
                r = ((backgroundColorInt >> 24) & 0xFF)
                g = ((backgroundColorInt >> 16) & 0xFF)
                b = ((backgroundColorInt >> 8) & 0xFF)
                # a = (backgroundColorInt & 0xFF)
                backgroundColor = f"#{r:02x}{g:02x}{b:02x}"

            sizex, sizey = activeView.getSize()
            activeView.saveImage(fName, sizex, sizey, backgroundColor)

        # From the "TechDraw" view.
        elif str(activeView) == "MDI view page":
            mainWindow = FreeCADGui.getMainWindow()
            mdiArea = mainWindow.findChild(QtWidgets.QMdiArea)
            activeSubWindow = mdiArea.activeSubWindow()

            if not activeSubWindow:
                self.parent.statusMessage(f"\"{self.modulePath}\": No active MDI sub-window found.")
                return

            viewWidget = activeSubWindow.widget()
            newPixmap = viewWidget.grab()
            newPixmap.save(fName, "PNG")

        else:
            self.parent.statusMessage(f"\"{self.modulePath}\": View is not supported.")
            return

        self.parent.statusMessage(f"Done \"{self.modulePath}\".")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Take a screenshot of the current view and save that."

        return aboutStr
# ==============================================================================
