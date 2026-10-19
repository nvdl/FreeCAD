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
from PIL import Image
from PySide import QtWidgets

import FreeCAD
import FreeCADGui
# ==============================================================================
class CustomScript:

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

        fName, selectedFilter = self.parent.fileSaveDialog(
            "Please specify the destination file.",
            filters
        )

        if fName == "":
            self.parent.statusMessage(f"\"{self.modulePath}\": Canceled.")
            return

        if not fName.endswith(".png"):
            fName = f"{fName}.png"

        padding = -1

        # From the 3D view.
        if str(activeView) == "View3DInventor":
            text, status = self.parent.inputDialog(
                self.modulePath, "Please specify the padding (-1: Skip):", "-1"
            )

            if not status:
                return

            padding = int(text)

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

            if padding == -1:
                activeView.saveImage(fName, sizex, sizey, backgroundColor)
            else:
                activeView.saveImage(fName, sizex, sizey, "Transparent")
                self.crop(fName, padding, backgroundColor)

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
    def crop(self, fName: str, padding: int, backgroundColor: str) -> None:

        with Image.open(fName) as img:
            if "A" not in img.getbands():
                self.parent.statusMessage(f"Padding failed: \"{self.modulePath}\".")
                return

            bbox = img.getchannel("A").getbbox()

            if bbox is None:
                self.parent.statusMessage(f"Padding failed: \"{self.modulePath}\".")
                return

            left, upper, right, lower = bbox
            imgCropped = img.crop((left, upper, right, lower))

            paddedSize = (
                imgCropped.size[0] + (padding * 2),
                imgCropped.size[1] + (padding * 2)
            )

            namesToValues = {
                "Transparent": "#00000000",
                "Black": "#000000ff",
                "White": "#ffffffff"
            }

            backgroundColor = namesToValues.get(backgroundColor, backgroundColor)

            imgBackground = Image.new("RGBA", paddedSize, backgroundColor)
            imgBackground.paste(imgCropped, (padding, padding), imgCropped)
            imgBackground.save(fName)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Take a screenshot of the current view and save that."

        return aboutStr
# ==============================================================================
