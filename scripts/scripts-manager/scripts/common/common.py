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
# ==============================================================================
def getSelection(extended: bool) -> "list[FreeCADGui.SelectionObject] | list[FreeCAD.DocumentObject]":

    if extended:
        selObjs = FreeCADGui.Selection.getSelectionEx()
    else:
        selObjs = FreeCADGui.Selection.getSelection()

    return selObjs
# ==============================================================================
def getAllObjects() -> list[FreeCAD.DocumentObject]:

    return FreeCAD.ActiveDocument.Objects
# ==============================================================================
def getGroup(groupLabel: str, autoCreate: bool) -> FreeCAD.DocumentObject:

    group = None

    selection = FreeCAD.ActiveDocument.getObjectsByLabel(groupLabel)

    if len(selection):
        for obj in selection:
            if obj.TypeId == "App::DocumentObjectGroup":
                group = obj
                break
    else:
        if autoCreate:
            group = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", groupLabel)

    return group
# ==============================================================================
def addToGroup(objs: tuple[FreeCAD.DocumentObject], groupLabel: str) -> None:

    group = getGroup(groupLabel, True)
    assert group is not None

    for obj in objs:
        group.addObject(obj)
# ==============================================================================
