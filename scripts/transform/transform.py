#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==================================================================================================
'''
***************************************************************************
*                                                                         *
*   Author: Naveed Alam.                                                  *
*   Date: 28th of August, 2024                                            *
*   Email: naveedguy ayt gmail dot com                                    *
*   License: https://github.com/FreeCAD/FreeCAD/blob/main/LICENSE         *
*                                                                         *
***************************************************************************
*                                                                         *
*   This macro allows for positioning of a selection of objects.          *
*   It adds temporary bounding boxes and center marks before moving       *
*   the objects and removes them after the translation is complete.       *
*                                                                         *
*   It supports:                                                          *
*   - Translation of a single, multiple or a group (FreeCAD group)        *
*     of objects.                                                         *
*   - Snapping to center and origin marks (after adding them).            *
*   - Addition of "edge-to-edge", "vertex-to-vertex" and                  *
*     "vertex-to-edge" dimensions.                                        *
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
# ==================================================================================================
import os
import sys
from dataclasses import dataclass
from importlib import import_module
from traceback import format_exc

from PySide.QtGui import *
from PySide.QtCore import *

import FreeCAD
import FreeCADGui
import Part
import Draft
# ==================================================================================================
__title__ = "Transform"
__version__ = "2.0"
__date__ = "28/08/2024"
__author__ = "Naveed Alam"
__Requires__ = "Freecad 0.21"
__Status__ = "stable"
__Comment__ = "This macro allows for translating selected object(s) or group(s) of objects."
__url__ = "http://www.freecadweb.org/"
__Web__ = "http://www.freecadweb.org/"
__Wiki__ = "http://www.freecadweb.org/wiki/"
__Icon__ = ""
__IconW__ = ""
__Help__ = ""
# ==================================================================================================
@dataclass
class ObjectParameters:
    """Class to represent a design object's parameters."""
    object: "Part::Feature"
    base: "FreeCAD.Vector"
    center: "FreeCAD.Vector"
    boundingBoxEnabled: bool
# ==================================================================================================
class MacroWindow(QMainWindow):

    def __init__(self, parent=None) -> None:

        QMainWindow.__init__(self, parent)

        self.GROUP_LABEL_CENTER_LINES = "lines_center"
        self.GROUP_LABEL_TEMP_CENTER_LINES = "lines_temp_center"
        self.GROUP_LABEL_ORIGIN_LINES = "lines_origin"

        self.LINE_CENTER_NAME_PREFIX = "line_center"
        self.LINE_CENTER_X_LABEL_PREFIX = f"{self.LINE_CENTER_NAME_PREFIX}_cx"
        self.LINE_CENTER_Y_LABEL_PREFIX = f"{self.LINE_CENTER_NAME_PREFIX}_cy"
        self.LINE_CENTER_Z_LABEL_PREFIX = f"{self.LINE_CENTER_NAME_PREFIX}_cz"

        self.LINE_ORIGIN_NAME_SUFFIX = "origin"
        self.LINE_ORIGIN_X_NAME = f"{self.LINE_CENTER_X_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"
        self.LINE_ORIGIN_Y_NAME = f"{self.LINE_CENTER_Y_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"
        self.LINE_ORIGIN_Z_NAME = f"{self.LINE_CENTER_Z_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{__title__} v{__version__}")

        self.ui.lbldX.setToolTip("Total translation along the x axis.")
        self.ui.lbldY.setToolTip("Total translation along the y axis.")
        self.ui.lbldZ.setToolTip("Total translation along the z axis.")
        self.ui.lblStep.setToolTip("Step size along any axis.")
        self.ui.lblSnap.setToolTip("Snapping distance for any axis.")

        self.freeCADGuiMainWin = FreeCADGui.getMainWindow()

        self.drawStyleActions = {
            0: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleAsIs"),
            1: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStylePoints"),
            2: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleWireframe"),
            3: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleHiddenLine"),
            4: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleNoShading"),
            5: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleShaded"),
            6: self.freeCADGuiMainWin.findChild(QAction, "Std_DrawStyleFlatLines")
        }

        self.drawStyleRevertAction = None

        self.ui.btnResetTransforms.clicked.connect(self.btnResetTransformsClicked)
        self.ui.btnOrthographic.clicked.connect(self.btnOrthographicClicked)
        self.ui.btnPerspective.clicked.connect(self.btnPerspectiveClicked)
        self.ui.btnAddCenterMark.clicked.connect(self.btnAddCenterMarkClicked)
        self.ui.btnToggleOriginMark.clicked.connect(self.btnToggleOriginMarkClicked)
        self.ui.btnDefaultLineColor.clicked.connect(self.btnDefaultLineColorClicked)

        self.ui.btnAddDimensionX.clicked.connect(self.btnAddDimensionClicked)
        self.ui.btnAddDimensionY.clicked.connect(self.btnAddDimensionClicked)
        self.ui.btnAddDimensionZ.clicked.connect(self.btnAddDimensionClicked)

        self.ui.sldTranslateX.valueChanged.connect(self.sldTranslateXChanged)
        self.ui.sldTranslateY.valueChanged.connect(self.sldTranslateYChanged)
        self.ui.sldTranslateZ.valueChanged.connect(self.sldTranslateZChanged)
        self.ui.sldTranslateDelta.valueChanged.connect(self.sldTranslateDeltaChanged)
        self.ui.sldSnapDistance.valueChanged.connect(self.sldSnapDistanceChanged)

        self.ui.sldTranslateX.sliderPressed.connect(self.sldPressed)
        self.ui.sldTranslateY.sliderPressed.connect(self.sldPressed)
        self.ui.sldTranslateZ.sliderPressed.connect(self.sldPressed)

        self.ui.sldTranslateX.sliderReleased.connect(self.sldReleased)
        self.ui.sldTranslateY.sliderReleased.connect(self.sldReleased)
        self.ui.sldTranslateZ.sliderReleased.connect(self.sldReleased)

        self.ui.chkAlwaysOnTop.clicked.connect(self.chkAlwaysOnTopClicked)

        self.transformActive = False

        self.axisXTranslation = self.axisYTranslation = self.axisZTranslation = 0

        self.deltaTranslation = float(10 ** self.ui.sldTranslateDelta.value())
        self.snapDistance = float(10 ** self.ui.sldSnapDistance.value())

        # Synchronize the labels.
        self.sldTranslateDeltaChanged()
        self.ui.sldSnapDistance.setValue(1)

        self.markerLineColor = (150 / 255.0, 150 / 255.0, 150 / 255.0, 0.0)
        self.markerLineWidth = 2

        self.snapLineColor = (0.0, 1.0, 1.0, 0.0)
        self.snapLineWidth = 4

        self.axesMarkerLineLength = 500

        self.chkAlwaysOnTopClicked()

        self.show()
# ==================================================================================================
    def chkAlwaysOnTopClicked(self) -> None:

        flags = self.windowFlags()

        if self.ui.chkAlwaysOnTop.isChecked():
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & (~Qt.WindowStaysOnTopHint))

        self.show()
# ==================================================================================================
    def sldTranslateXChanged(self) -> None:

        self.translateSelection(self.ui.sldTranslateX.value(), 0, 0)
# ==================================================================================================
    def sldTranslateYChanged(self) -> None:

        self.translateSelection(0, self.ui.sldTranslateY.value(), 0)
# ==================================================================================================
    def sldTranslateZChanged(self) -> None:

        self.translateSelection(0, 0, self.ui.sldTranslateZ.value())
# ==================================================================================================
    def sldTranslateDeltaChanged(self) -> None:

        self.deltaTranslation = float(10 ** self.ui.sldTranslateDelta.value())
        self.updateTranslationLabels()
# ==================================================================================================
    def sldSnapDistanceChanged(self) -> None:

        self.snapDistance = float(10 ** self.ui.sldSnapDistance.value())
        self.updateTranslationLabels()
# ==================================================================================================
    def getSelectedObjects(self, extended=False) -> list[ObjectParameters]:

        if extended:
            objs2 = FreeCADGui.Selection.getSelectionEx()
        else:
            objs2 = FreeCADGui.Selection.getSelection()

        objs = []

        allowedTypeIds = ["Part", "Mesh", "Image"]

        for obj in objs2:
            if extended:
                obj = obj.Object

            if obj.TypeId == "App::DocumentObjectGroup":
                for subObj in obj.Group:
                    try:
                        if subObj.TypeId.split("::")[0] in allowedTypeIds:
                            objs.append(subObj)
                        else:
                            App.Console.PrintMessage(f"Not selecting \"{subObj.Label}\".\n")
                    except:
                        App.Console.PrintMessage(f"Exception; cannot select \"{subObj.Label}\".\n")
            else:
                if obj.TypeId.split("::")[0] in allowedTypeIds:
                    objs.append(obj)
                else:
                    App.Console.PrintMessage(f"Not selecting \"{obj.Label}\".\n")

        selObjs = [ObjectParameters(obj,
                                    obj.Placement.Base,
                                    self.getCenter(obj),
                                    obj.ViewObject.BoundingBox)
                   for obj in objs]

        return selObjs
# ==================================================================================================
    def sldPressed(self) -> None:

        self.centerLines = []

        self.selectedObjsParams = self.getSelectedObjects(extended=True)
        self.selectedObjsParams += self.getSelectedObjects(extended=False)

        if self.ui.chkBoundingBoxes.isChecked():
            for objParams in self.selectedObjsParams:
                objParams.object.ViewObject.BoundingBox = True

        self.centerLinesParams = self.getGroupObjects(self.GROUP_LABEL_CENTER_LINES)
        self.centerLinesParams += self.getGroupObjects(self.GROUP_LABEL_ORIGIN_LINES)

        # Transformation has started.
        self.transformActive = True

        if self.ui.chkWireFrame.isChecked():
            for i in range(7):
                action = self.drawStyleActions[i]
                if action.isChecked():
                    self.drawStyleRevertAction = action
                    break

            self.drawStyleActions[2].trigger()
        else:
            self.drawStyleRevertAction = None

        if self.ui.chkCenterMarks.isChecked():
            self.drawCenterMarks(0, 0, 0, True)
# ==================================================================================================
    def drawCenterMarks(self, dx, dy, dz, add) -> None:

        for i, objParams in enumerate(self.selectedObjsParams):
            lines = self.drawCenterMark(i, self.getCenter(objParams.object), (dx, dy, dz), "", add)
            if add:
                self.centerLines.append(lines)
                self.addToGroup(lines, self.GROUP_LABEL_TEMP_CENTER_LINES)
# ==================================================================================================
    # Draw and move center marks.

    def drawCenterMark(self, i, p1, offset, objectLabel, add) -> list:

        dx = offset[0]
        dy = offset[1]
        dz = offset[2]

        p2 = FreeCAD.Vector(self.axesMarkerLineLength, 0, 0)
        p3 = FreeCAD.Vector(0, self.axesMarkerLineLength, 0)
        p4 = FreeCAD.Vector(0, 0, self.axesMarkerLineLength)

        lines = []

        start1 = (p1 - p2) + FreeCAD.Vector(dx, dy, dz)
        end1 = (p1 + p2) + FreeCAD.Vector(dx, dy, dz)

        start2 = (p1 - p3) + FreeCAD.Vector(dx, dy, dz)
        end2 = (p1 + p3) + FreeCAD.Vector(dx, dy, dz)

        start3 = (p1 - p4) + FreeCAD.Vector(dx, dy, dz)
        end3 = (p1 + p4) + FreeCAD.Vector(dx, dy, dz)

        linesSpecs = [
            (0, self.LINE_CENTER_X_LABEL_PREFIX, start1, end1),
            (1, self.LINE_CENTER_Y_LABEL_PREFIX, start2, end2),
            (2, self.LINE_CENTER_Z_LABEL_PREFIX, start3, end3)
        ]

        for index, labelPrefix, start, end in linesSpecs:
            if add:
                line = App.ActiveDocument.addObject("Part::Line", self.LINE_CENTER_NAME_PREFIX)
                line.ViewObject.LineColor = self.markerLineColor
                line.ViewObject.LineWidth = self.markerLineWidth

                if objectLabel != "":
                    line.Label = f"{labelPrefix}_{objectLabel}"
                else:
                    line.Label = f"{labelPrefix}"
            else:
                line = self.centerLines[i][index]

            line.X1 = start.x
            line.Y1 = start.y
            line.Z1 = start.z
            line.X2 = end.x
            line.Y2 = end.y
            line.Z2 = end.z

            lines.append(line)

        return lines
# ==================================================================================================
    def addRemoveOriginMark(self, add) -> None:

        if add:
            l1 = App.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_X_NAME)
            l1.X1 = -self.axesMarkerLineLength
            l1.X2 = self.axesMarkerLineLength
            l1.Y1 = l1.Z1 = l1.Y2 = l1.Z2 = 0

            l2 = App.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_Y_NAME)
            l2.Y1 = -self.axesMarkerLineLength
            l2.Y2 = self.axesMarkerLineLength
            l2.X1 = l2.Z1 = l2.X2 = l2.Z2 = 0

            l3 = App.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_Z_NAME)
            l3.Z1 = -self.axesMarkerLineLength
            l3.Z2 = self.axesMarkerLineLength
            l3.X1 = l3.Y1 = l3.X2 = l3.Y2 = 0

            self.addToGroup((l1, l2, l3), self.GROUP_LABEL_ORIGIN_LINES)
            self.formatOriginMark()
        else:
            self.removeGroup(self.GROUP_LABEL_ORIGIN_LINES)
# ==================================================================================================
    def formatOriginMark(self) -> None:

        objsParams = self.getGroupObjects(self.GROUP_LABEL_ORIGIN_LINES)

        for objParams in objsParams:
            obj = objParams.object

            if obj.Label == self.LINE_ORIGIN_X_NAME:
                obj.ViewObject.LineColor = (1.0, 0.0, 0.0, 0.0)
                obj.ViewObject.LineWidth = self.markerLineWidth

            elif obj.Label == self.LINE_ORIGIN_Y_NAME:
                obj.ViewObject.LineColor = (0.0, 1.0, 0.0, 0.0)
                obj.ViewObject.LineWidth = self.markerLineWidth

            elif obj.Label == self.LINE_ORIGIN_Z_NAME:
                obj.ViewObject.LineColor = (0.0, 0.0, 1.0, 0.0)
                obj.ViewObject.LineWidth = self.markerLineWidth
# ==================================================================================================
    def getGroup(self, groupLabel, autoCreate):

        group = None

        selection = App.ActiveDocument.getObjectsByLabel(groupLabel)

        if len(selection):
            for obj in selection:
                if obj.TypeId == "App::DocumentObjectGroup":
                    group = obj
                    break
        else:
            if autoCreate:
                group = App.ActiveDocument.addObject("App::DocumentObjectGroup", groupLabel)

        return group
# ==================================================================================================
    def removeGroup(self, groupLabel) -> None:

        objsParams = self.getGroupObjects(groupLabel)

        for objParams in objsParams:
            self.removeObject(objParams.object)

        self.removeObjectsByLabel(groupLabel)
# ==================================================================================================
    def addToGroup(self, objs, groupLabel) -> None:

        group = self.getGroup(groupLabel, True)

        for obj in objs:
            group.addObject(obj)
# ==================================================================================================
    def getGroupObjects(self, groupLabel) -> list[ObjectParameters]:

        group = self.getGroup(groupLabel, False)

        if group == None:
            return []

        objs = []

        for obj in group.Group:
            if type(obj.Shape) != Part.Face:
                objs.append(obj)
            else:
                App.Console.PrintMessage(f"Not selecting \"{obj.Label}\".\n")

        groupObjs = [ObjectParameters(obj,
                                      obj.Placement.Base,
                                      self.getCenter(obj),
                                      obj.ViewObject.BoundingBox)
                     for obj in objs]

        return groupObjs
# ==================================================================================================
    def btnAddCenterMarkClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        self.selectedObjsParams = self.getSelectedObjects(extended=True)

        if len(self.selectedObjsParams) == 0:
            self.ui.statusBar.showMessage("Nothing selected.")
            return

        for objParams in self.selectedObjsParams:
            obj = objParams.object

            l1, l2, l3 = self.drawCenterMark(0, self.getCenter(obj), (0, 0, 0), obj.Label, True)

            l1.ViewObject.LineColor = self.markerLineColor
            l2.ViewObject.LineColor = self.markerLineColor
            l3.ViewObject.LineColor = self.markerLineColor

            self.addToGroup((l1, l2, l3), self.GROUP_LABEL_CENTER_LINES)
# ==================================================================================================
    def btnToggleOriginMarkClicked(self) -> None:

        group = self.getGroup(self.GROUP_LABEL_ORIGIN_LINES, False)

        if group == None:
            self.addRemoveOriginMark(True)
        else:
            self.addRemoveOriginMark(False)
# ==================================================================================================
    def sldReleased(self) -> None:

        prevTransform = self.transformActive

        # Transformation has ended.
        self.transformActive = False

        self.ui.sldTranslateX.setValue(0)
        self.ui.sldTranslateY.setValue(0)
        self.ui.sldTranslateZ.setValue(0)

        self.updateTranslationLabels()

        if not prevTransform:
            return

        # Restore the status of bounding boxes.
        if self.ui.chkBoundingBoxes.isChecked():
            for objParams in self.selectedObjsParams:
                objParams.object.ViewObject.BoundingBox = objParams.boundingBoxEnabled

        if self.drawStyleRevertAction is not None:
            self.drawStyleRevertAction.trigger()

        self.removeGroup(self.GROUP_LABEL_TEMP_CENTER_LINES)

        # Clear snapping related highlighting.
        self.formatOriginMark()

        # Clear snapping related highlighting.
        for centerLine in self.centerLinesParams:
            lineCL = centerLine.object
            if not self.isOriginLine(lineCL.Label):
                lineCL.ViewObject.LineColor = self.markerLineColor
                lineCL.ViewObject.LineWidth = self.markerLineWidth

        if self.ui.chkAutoRecompute.isChecked():
            App.ActiveDocument.recompute()
# ==================================================================================================
    def btnResetTransformsClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        self.getSelectedObjects(extended=False)

        for objParam in self.selectedObjsParams:
            objParam.object.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 0), 0))

        App.ActiveDocument.recompute()
# ==================================================================================================
    def updateTranslationLabels(self) -> None:

        self.ui.lblTranslateX.setText(f"{self.axisXTranslation:g}")
        self.ui.lblTranslateY.setText(f"{self.axisYTranslation:g}")
        self.ui.lblTranslateZ.setText(f"{self.axisZTranslation:g}")
        self.ui.lblTranslateDelta.setText(f"{self.deltaTranslation:g}")
        self.ui.lblSnapDistance.setText(f"{self.snapDistance:g}")
# ==================================================================================================
    def translateSelection(self, x, y, z) -> None:

        self.ui.statusBar.clearMessage()

        if len(self.selectedObjsParams) == 0:
            self.ui.statusBar.showMessage("Nothing selected.")
            return

        if not self.transformActive:
            self.ui.sldTranslateX.setValue(0)
            self.ui.sldTranslateY.setValue(0)
            self.ui.sldTranslateZ.setValue(0)

            self.axisXTranslation = self.axisYTranslation = self.axisZTranslation = 0
            self.updateTranslationLabels()
            return

        for i in range(len(self.selectedObjsParams)):
            obj = self.selectedObjsParams[i].object

            # Use the base as a reference before moving started (updated when the slider is released).
            base = self.selectedObjsParams[i].base

            self.axisXTranslation = x * self.deltaTranslation
            self.axisYTranslation = y * self.deltaTranslation
            self.axisZTranslation = z * self.deltaTranslation

            if self.ui.chkSnap.isChecked():
                self.checkSnapping()

            newX = base.x + self.axisXTranslation
            newY = base.y + self.axisYTranslation
            newZ = base.z + self.axisZTranslation

            newBase = FreeCAD.Vector(newX, newY, newZ)

            obj.Placement.Base = newBase

            if self.ui.chkAutoUpdateView.isChecked():
                obj.ViewObject.update()

            if self.ui.chkCenterMarks.isChecked():
                self.drawCenterMarks(0, 0, 0, False)

            self.updateTranslationLabels()
# ==================================================================================================
    def checkSnapping(self) -> None:

        self.axisXTranslation2 = self.axisXTranslation
        self.axisYTranslation2 = self.axisYTranslation
        self.axisZTranslation2 = self.axisZTranslation

        for objParams in self.selectedObjsParams:
            # Use the center as a reference before moving starts (updated when the slider is released).
            center = objParams.center

            newCenterX = center[0] + self.axisXTranslation
            newCenterY = center[1] + self.axisYTranslation
            newCenterZ = center[2] + self.axisZTranslation

            snapped = False

            # Clear snapping related highlighting.
            self.formatOriginMark()

            for centerLine in self.centerLinesParams:
                lineCL = centerLine.object
                labelCL = lineCL.Label

                # Clear snapping related highlighting.
                if not self.isOriginLine(labelCL):
                    lineCL.ViewObject.LineColor = self.markerLineColor
                    lineCL.ViewObject.LineWidth = self.markerLineWidth

                if abs(self.axisXTranslation) > 0:
                    if labelCL.startswith(self.LINE_CENTER_Y_LABEL_PREFIX) or \
                            labelCL.startswith(self.LINE_CENTER_Z_LABEL_PREFIX):
                        xdiff = float(lineCL.X1) - newCenterX
                        if abs(xdiff) <= self.snapDistance:
                            self.axisXTranslation2 += xdiff
                            snapped = True

                elif abs(self.axisYTranslation) > 0:
                    if labelCL.startswith(self.LINE_CENTER_X_LABEL_PREFIX) or \
                            labelCL.startswith(self.LINE_CENTER_Z_LABEL_PREFIX):
                        ydiff = float(lineCL.Y1) - newCenterY
                        if abs(ydiff) <= self.snapDistance:
                            self.axisYTranslation2 += ydiff
                            snapped = True

                elif abs(self.axisZTranslation) > 0:
                    if labelCL.startswith(self.LINE_CENTER_X_LABEL_PREFIX) or \
                            labelCL.startswith(self.LINE_CENTER_Y_LABEL_PREFIX):
                        zdiff = float(lineCL.Z1) - newCenterZ
                        if abs(zdiff) <= self.snapDistance:
                            self.axisZTranslation2 += zdiff
                            snapped = True

                if snapped:
                    break

            if snapped:
                message = f"\"{objParams.object.Label}\" snapped to reference line \"{labelCL}\"."
                self.ui.statusBar.showMessage(message)

                lineCL.ViewObject.LineColor = self.snapLineColor
                lineCL.ViewObject.LineWidth = self.snapLineWidth

                self.axisXTranslation = self.axisXTranslation2
                self.axisYTranslation = self.axisYTranslation2
                self.axisZTranslation = self.axisZTranslation2

                break
# ==================================================================================================
    def btnAddDimensionClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        selection = Gui.Selection.getSelectionEx()

        obj1 = obj2 = None

        if len(selection) == 1:
            subObjs = selection[0].SubObjects

            if len(subObjs) == 2:
                obj1 = subObjs[0]
                obj2 = subObjs[1]

        elif len(selection) == 2:
            subObjs1 = selection[0].SubObjects
            subObjs2 = selection[1].SubObjects

            if len(subObjs1) == 1 and len(subObjs2) == 1:
                obj1 = subObjs1[0]
                obj2 = subObjs2[0]

        if obj1 == None or obj2 == None:
            self.ui.statusBar.showMessage("Please select two parts; edge or vertex.")
            return

        p1 = p2 = None

        if type(obj1) == Part.Vertex:
            p1 = FreeCAD.Vector(obj1.X, obj1.Y, obj1.Z)
        elif type(obj1) == Part.Edge:
            p1 = obj1.firstVertex().Point

        if type(obj2) == Part.Vertex:
            p2 = FreeCAD.Vector(obj2.X, obj2.Y, obj2.Z)
        elif type(obj2) == Part.Edge:
            p2 = obj2.firstVertex().Point

        if p1 == None or p2 == None:
            self.ui.statusBar.showMessage("Please select two parts; edge or vertex.")
            return

        dimensionType = str(self.sender().objectName())[-1:]

        if dimensionType == "X":
            p2 = FreeCAD.Vector(p2.x, p1.y, p1.z)
        elif dimensionType == "Y":
            p2 = FreeCAD.Vector(p1.x, p2.y, p1.z)
        elif dimensionType == "Z":
            p2 = FreeCAD.Vector(p1.x, p1.y, p2.z)
        else:
            return

        if p1 == p2:
            self.ui.statusBar.showMessage("Cannot add a dimension of zero length.")
            return

        d = Draft.make_dimension(p1, p2)

        dv = d.ViewObject

        dv.ArrowType = 0
        dv.LineColor = self.markerLineColor
# ==================================================================================================
    def btnOrthographicClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        Gui.activeDocument().activeView().setCameraType("Orthographic")
# ==================================================================================================
    def btnPerspectiveClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        Gui.activeDocument().activeView().setCameraType("Perspective")
# ==================================================================================================
    def btnDefaultLineColorClicked(self) -> None:

        self.ui.statusBar.clearMessage()

        r = self.markerLineColor[0] * 255
        g = self.markerLineColor[1] * 255
        b = self.markerLineColor[2] * 255

        color = QColorDialog.getColor(QColor(r, g, b), None)

        r = color.red()
        g = color.green()
        b = color.blue()

        # "r", "g" and "b" are zero when the dialog is canceled.
        if not (r == g == b == 0):
            self.markerLineColor = (r / 255.0, g / 255.0, b / 255.0, 0.0)
# ==================================================================================================
    def removeObject(self, obj) -> None:

        App.ActiveDocument.removeObject(obj.Name)
# ==================================================================================================
    def removeObjects(self, objs) -> None:

        for obj in objs:
            self.removeObject(obj)
# ==================================================================================================
    def removeObjectsByLabel(self, label) -> None:

        objs = App.ActiveDocument.getObjectsByLabel(label)

        for obj in objs:
            self.removeObject(obj)
# ==================================================================================================
    def isOriginLine(self, label):

        return label in [self.LINE_ORIGIN_X_NAME, self.LINE_ORIGIN_Y_NAME, self.LINE_ORIGIN_Z_NAME]
# ==================================================================================================
    def getCenter(self, obj) -> "FreeCAD.Vector":

        if obj.TypeId == "Mesh::Feature":
            center = obj.Mesh.BoundBox.Center
        elif obj.TypeId == "Image::ImagePlane":
            center = obj.Placement.Base
        else:
            center = obj.Shape.BoundBox.Center

        return center
# ===========================================================================
    def getAllCenters(self) -> list["FreeCAD.Vector"]:

        centers = []

        for objParams in self.selectedObjsParams:
            centers.append(self.getCenter(objParams.object))

        return centers
# ===========================================================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        MainWindow.resize(460, 480)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(460, 480))
        MainWindow.setMaximumSize(QSize(460, 480))
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabMain = QTabWidget(self.centralwidget)
        self.tabMain.setObjectName(u"tabMain")
        self.tabMain.setEnabled(True)
        self.tabMain.setGeometry(QRect(0, 0, 671, 461))
        self.tabMain.setIconSize(QSize(16, 16))
        self.tabMain.setElideMode(Qt.ElideNone)
        self.tabMain.setDocumentMode(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.btnResetTransforms = QPushButton(self.tab)
        self.btnResetTransforms.setObjectName(u"btnResetTransforms")
        self.btnResetTransforms.setEnabled(True)
        self.btnResetTransforms.setGeometry(QRect(310, 160, 140, 40))
        self.btnResetTransforms.setMinimumSize(QSize(0, 0))
        self.btnResetTransforms.setStyleSheet(u"")
        self.sldTranslateX = QSlider(self.tab)
        self.sldTranslateX.setObjectName(u"sldTranslateX")
        self.sldTranslateX.setGeometry(QRect(60, 0, 310, 40))
        self.sldTranslateX.setMinimum(-50)
        self.sldTranslateX.setMaximum(50)
        self.sldTranslateX.setPageStep(1)
        self.sldTranslateX.setOrientation(Qt.Horizontal)
        self.sldTranslateY = QSlider(self.tab)
        self.sldTranslateY.setObjectName(u"sldTranslateY")
        self.sldTranslateY.setGeometry(QRect(60, 30, 310, 40))
        self.sldTranslateY.setMinimum(-50)
        self.sldTranslateY.setMaximum(50)
        self.sldTranslateY.setPageStep(1)
        self.sldTranslateY.setOrientation(Qt.Horizontal)
        self.sldTranslateZ = QSlider(self.tab)
        self.sldTranslateZ.setObjectName(u"sldTranslateZ")
        self.sldTranslateZ.setGeometry(QRect(60, 60, 310, 40))
        self.sldTranslateZ.setMinimum(-50)
        self.sldTranslateZ.setMaximum(50)
        self.sldTranslateZ.setPageStep(1)
        self.sldTranslateZ.setOrientation(Qt.Horizontal)
        self.sldTranslateDelta = QSlider(self.tab)
        self.sldTranslateDelta.setObjectName(u"sldTranslateDelta")
        self.sldTranslateDelta.setGeometry(QRect(60, 90, 310, 40))
        self.sldTranslateDelta.setMinimum(-9)
        self.sldTranslateDelta.setMaximum(9)
        self.sldTranslateDelta.setPageStep(1)
        self.sldTranslateDelta.setOrientation(Qt.Horizontal)
        self.chkWireFrame = QCheckBox(self.tab)
        self.chkWireFrame.setObjectName(u"chkWireFrame")
        self.chkWireFrame.setGeometry(QRect(10, 340, 180, 30))
        self.lbldX = QLabel(self.tab)
        self.lbldX.setObjectName(u"lbldX")
        self.lbldX.setGeometry(QRect(10, 10, 40, 20))
        self.lbldY = QLabel(self.tab)
        self.lbldY.setObjectName(u"lbldY")
        self.lbldY.setGeometry(QRect(10, 40, 40, 20))
        self.lbldZ = QLabel(self.tab)
        self.lbldZ.setObjectName(u"lbldZ")
        self.lbldZ.setGeometry(QRect(10, 70, 40, 20))
        self.lblStep = QLabel(self.tab)
        self.lblStep.setObjectName(u"lblStep")
        self.lblStep.setGeometry(QRect(10, 100, 40, 20))
        self.lblTranslateX = QLabel(self.tab)
        self.lblTranslateX.setObjectName(u"lblTranslateX")
        self.lblTranslateX.setGeometry(QRect(390, 10, 60, 20))
        self.lblTranslateZ = QLabel(self.tab)
        self.lblTranslateZ.setObjectName(u"lblTranslateZ")
        self.lblTranslateZ.setGeometry(QRect(390, 70, 60, 20))
        self.lblTranslateY = QLabel(self.tab)
        self.lblTranslateY.setObjectName(u"lblTranslateY")
        self.lblTranslateY.setGeometry(QRect(390, 40, 60, 20))
        self.lblTranslateDelta = QLabel(self.tab)
        self.lblTranslateDelta.setObjectName(u"lblTranslateDelta")
        self.lblTranslateDelta.setGeometry(QRect(390, 100, 60, 20))
        self.btnAddDimensionZ = QPushButton(self.tab)
        self.btnAddDimensionZ.setObjectName(u"btnAddDimensionZ")
        self.btnAddDimensionZ.setEnabled(True)
        self.btnAddDimensionZ.setGeometry(QRect(310, 260, 140, 40))
        self.btnAddDimensionZ.setMinimumSize(QSize(0, 0))
        self.btnAddDimensionZ.setStyleSheet(u"")
        self.btnOrthographic = QPushButton(self.tab)
        self.btnOrthographic.setObjectName(u"btnOrthographic")
        self.btnOrthographic.setEnabled(True)
        self.btnOrthographic.setGeometry(QRect(10, 160, 140, 40))
        self.btnOrthographic.setMinimumSize(QSize(0, 0))
        self.btnOrthographic.setStyleSheet(u"")
        self.btnPerspective = QPushButton(self.tab)
        self.btnPerspective.setObjectName(u"btnPerspective")
        self.btnPerspective.setEnabled(True)
        self.btnPerspective.setGeometry(QRect(10, 210, 140, 40))
        self.btnPerspective.setMinimumSize(QSize(0, 0))
        self.btnPerspective.setStyleSheet(u"")
        self.btnAddCenterMark = QPushButton(self.tab)
        self.btnAddCenterMark.setObjectName(u"btnAddCenterMark")
        self.btnAddCenterMark.setEnabled(True)
        self.btnAddCenterMark.setGeometry(QRect(160, 160, 140, 40))
        self.btnAddCenterMark.setMinimumSize(QSize(0, 0))
        self.btnAddCenterMark.setStyleSheet(u"")
        self.chkSnap = QCheckBox(self.tab)
        self.chkSnap.setObjectName(u"chkSnap")
        self.chkSnap.setGeometry(QRect(10, 370, 180, 30))
        self.chkSnap.setChecked(True)
        self.btnDefaultLineColor = QPushButton(self.tab)
        self.btnDefaultLineColor.setObjectName(u"btnDefaultLineColor")
        self.btnDefaultLineColor.setEnabled(True)
        self.btnDefaultLineColor.setGeometry(QRect(310, 210, 140, 40))
        self.btnDefaultLineColor.setMinimumSize(QSize(0, 0))
        self.btnDefaultLineColor.setStyleSheet(u"")
        self.chkCenterMarks = QCheckBox(self.tab)
        self.chkCenterMarks.setObjectName(u"chkCenterMarks")
        self.chkCenterMarks.setGeometry(QRect(160, 340, 180, 30))
        self.chkCenterMarks.setChecked(True)
        self.chkAutoUpdateView = QCheckBox(self.tab)
        self.chkAutoUpdateView.setObjectName(u"chkAutoUpdateView")
        self.chkAutoUpdateView.setGeometry(QRect(10, 400, 180, 30))
        self.chkAutoRecompute = QCheckBox(self.tab)
        self.chkAutoRecompute.setObjectName(u"chkAutoRecompute")
        self.chkAutoRecompute.setGeometry(QRect(160, 370, 180, 30))
        self.chkAutoRecompute.setChecked(True)
        self.sldSnapDistance = QSlider(self.tab)
        self.sldSnapDistance.setObjectName(u"sldSnapDistance")
        self.sldSnapDistance.setGeometry(QRect(60, 120, 310, 40))
        self.sldSnapDistance.setMinimum(-9)
        self.sldSnapDistance.setMaximum(9)
        self.sldSnapDistance.setPageStep(1)
        self.sldSnapDistance.setOrientation(Qt.Horizontal)
        self.lblSnapDistance = QLabel(self.tab)
        self.lblSnapDistance.setObjectName(u"lblSnapDistance")
        self.lblSnapDistance.setGeometry(QRect(390, 130, 60, 20))
        self.lblSnap = QLabel(self.tab)
        self.lblSnap.setObjectName(u"lblSnap")
        self.lblSnap.setGeometry(QRect(10, 130, 40, 20))
        self.chkBoundingBoxes = QCheckBox(self.tab)
        self.chkBoundingBoxes.setObjectName(u"chkBoundingBoxes")
        self.chkBoundingBoxes.setGeometry(QRect(160, 310, 180, 30))
        self.chkBoundingBoxes.setChecked(True)
        self.chkAlwaysOnTop = QCheckBox(self.tab)
        self.chkAlwaysOnTop.setObjectName(u"chkAlwaysOnTop")
        self.chkAlwaysOnTop.setGeometry(QRect(10, 310, 180, 30))
        self.btnAddDimensionY = QPushButton(self.tab)
        self.btnAddDimensionY.setObjectName(u"btnAddDimensionY")
        self.btnAddDimensionY.setEnabled(True)
        self.btnAddDimensionY.setGeometry(QRect(160, 260, 140, 40))
        self.btnAddDimensionY.setMinimumSize(QSize(0, 0))
        self.btnAddDimensionY.setStyleSheet(u"")
        self.btnAddDimensionX = QPushButton(self.tab)
        self.btnAddDimensionX.setObjectName(u"btnAddDimensionX")
        self.btnAddDimensionX.setEnabled(True)
        self.btnAddDimensionX.setGeometry(QRect(10, 260, 140, 40))
        self.btnAddDimensionX.setMinimumSize(QSize(0, 0))
        self.btnAddDimensionX.setStyleSheet(u"")
        self.btnToggleOriginMark = QPushButton(self.tab)
        self.btnToggleOriginMark.setObjectName(u"btnToggleOriginMark")
        self.btnToggleOriginMark.setEnabled(True)
        self.btnToggleOriginMark.setGeometry(QRect(160, 210, 140, 40))
        self.btnToggleOriginMark.setMinimumSize(QSize(0, 0))
        self.btnToggleOriginMark.setStyleSheet(u"")
        self.tabMain.addTab(self.tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        QWidget.setTabOrder(self.sldTranslateX, self.sldTranslateY)
        QWidget.setTabOrder(self.sldTranslateY, self.sldTranslateZ)
        QWidget.setTabOrder(self.sldTranslateZ, self.sldTranslateDelta)
        QWidget.setTabOrder(self.sldTranslateDelta, self.btnResetTransforms)
        QWidget.setTabOrder(self.btnResetTransforms, self.btnAddDimensionZ)
        QWidget.setTabOrder(self.btnAddDimensionZ, self.btnAddCenterMark)
        QWidget.setTabOrder(self.btnAddCenterMark, self.btnOrthographic)
        QWidget.setTabOrder(self.btnOrthographic, self.btnPerspective)
        QWidget.setTabOrder(self.btnPerspective, self.chkWireFrame)
        QWidget.setTabOrder(self.chkWireFrame, self.chkSnap)
        QWidget.setTabOrder(self.chkSnap, self.tabMain)

        self.retranslateUi(MainWindow)

        self.tabMain.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.btnResetTransforms.setText(QCoreApplication.translate("MainWindow", u"Reset Transforms", None))
        self.chkWireFrame.setText(QCoreApplication.translate("MainWindow", u"Wireframe mode", None))
        self.lbldX.setText(QCoreApplication.translate("MainWindow", u"dX", None))
        self.lbldY.setText(QCoreApplication.translate("MainWindow", u"dY", None))
        self.lbldZ.setText(QCoreApplication.translate("MainWindow", u"dZ", None))
        self.lblStep.setText(QCoreApplication.translate("MainWindow", u"Step", None))
        self.lblTranslateX.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.lblTranslateZ.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.lblTranslateY.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.lblTranslateDelta.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.btnAddDimensionZ.setText(QCoreApplication.translate("MainWindow", u"Add Dimension Z", None))
        self.btnOrthographic.setText(QCoreApplication.translate("MainWindow", u"Orthographic View", None))
        self.btnPerspective.setText(QCoreApplication.translate("MainWindow", u"Perspective View", None))
        self.btnAddCenterMark.setText(QCoreApplication.translate("MainWindow", u"Add Center Mark", None))
        self.chkSnap.setText(QCoreApplication.translate("MainWindow", u"Snap to markers", None))
        self.btnDefaultLineColor.setText(QCoreApplication.translate("MainWindow", u"Set Line Color", None))
        self.chkCenterMarks.setText(QCoreApplication.translate("MainWindow", u"Draw center marks", None))
        self.chkAutoUpdateView.setText(QCoreApplication.translate("MainWindow", u"Auto update view", None))
        self.chkAutoRecompute.setText(QCoreApplication.translate("MainWindow", u"Auto recompute", None))
        self.lblSnapDistance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lblSnap.setText(QCoreApplication.translate("MainWindow", u"Snap", None))
        self.chkBoundingBoxes.setText(QCoreApplication.translate("MainWindow", u"Draw bounding boxes", None))
        self.chkAlwaysOnTop.setText(QCoreApplication.translate("MainWindow", u"Always on top", None))
        self.btnAddDimensionY.setText(QCoreApplication.translate("MainWindow", u"Add Dimension Y", None))
        self.btnAddDimensionX.setText(QCoreApplication.translate("MainWindow", u"Add Dimension X", None))
        self.btnToggleOriginMark.setText(QCoreApplication.translate("MainWindow", u"Toggle Origin Mark", None))

        self.tabMain.setTabText(self.tabMain.indexOf(self.tab),
                                QCoreApplication.translate("MainWindow", u"Transform", None))
# ===========================================================================
FreeCADRootWindow = Gui.getMainWindow()
macroWindow = MacroWindow()
# ===========================================================================
