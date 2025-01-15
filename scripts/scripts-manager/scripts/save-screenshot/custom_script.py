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
# ==============================================================================
    def run(self) -> None:

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        activeView = FreeCADGui.activeDocument().activeView()

        backgroundColor = "Transparent"
        # backgroundColor = "White"
        # backgroundColor = "Black"

        sizex, sizey = activeView.getSize()

        # filters = "PNG images (*.png);;JPG images (*.jpg)"
        filters = "PNG images (*.png)"

        fName, selectedFilter = self.parent.fileSaveDialog("Please specify the destination file.", filters)

        if fName != "":
            activeView.saveImage(fName, sizex, sizey, backgroundColor)
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Take a screenshot of the current view and save that."

        return aboutStr
# ==============================================================================
