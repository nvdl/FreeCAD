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
*   This macro allows for positioning of a selection of objects.          *
*   It adds temporary bounding boxes and center marks before moving       *
*   the objects and removes them after the translation is complete.       *
*                                                                         *
*   It supports:                                                          *
*   - Translation of a single, multiple or a group (FreeCAD group)        *
*     of objects.                                                         *
*   - Snapping to center, origin and grid marks (after adding them).      *
*   - Changing line colors of objects under translation (highlighting).   *
*   - Toggling transparencies of all objects (x-ray mode).                *
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
from dataclasses import dataclass
from typing import Any
from traceback import format_exc

from PySide.QtGui import *
from PySide.QtCore import *

import FreeCAD
import FreeCADGui
import Part
# ==================================================================================================
__title__ = "Transform"
__version__ = "2.9"
__date__ = "21/01/2026"
__author__ = "Naveed Alam"
__Requires__ = "Freecad 1.0.0"
__Status__ = "stable"
__Comment__ = "This macro allows for translating selected object(s) or group(s) of objects."
__url__ = "http://www.freecadweb.org/"
__Web__ = "http://www.freecadweb.org/"
__Wiki__ = "http://www.freecadweb.org/wiki/"
__License__ = "LGPL-2.0-or-later"
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
    lineColor: tuple[float] | None
    lineWidth: float | None
    boundingBoxEnabled: bool | None
# ==================================================================================================
class MacroWindow(QMainWindow):

    def __init__(self, parent: QMainWindow) -> None:

        super().__init__(parent)

        self.GROUP_LABEL_CENTER_LINES = "lines_center"
        self.GROUP_LABEL_TEMP_CENTER_LINES = "lines_temp_center"
        self.GROUP_LABEL_ORIGIN_LINES = "lines_origin"
        self.GROUP_LABEL_GRID_LINES = "lines_grid"

        self.LINE_CENTER_NAME_PREFIX = "line_center"
        self.LINE_CENTER_LABEL_PREFIX = self.LINE_CENTER_NAME_PREFIX
        self.LINE_CENTER_X_LABEL_PREFIX = f"{self.LINE_CENTER_LABEL_PREFIX}_cx"
        self.LINE_CENTER_Y_LABEL_PREFIX = f"{self.LINE_CENTER_LABEL_PREFIX}_cy"
        self.LINE_CENTER_Z_LABEL_PREFIX = f"{self.LINE_CENTER_LABEL_PREFIX}_cz"

        self.LINE_GRID_LABEL_PREFIX = "line_grid"
        self.LINE_GRID_X_LABEL_PREFIX = f"{self.LINE_GRID_LABEL_PREFIX}_x"
        self.LINE_GRID_Y_LABEL_PREFIX = f"{self.LINE_GRID_LABEL_PREFIX}_y"
        self.LINE_GRID_Z_LABEL_PREFIX = f"{self.LINE_GRID_LABEL_PREFIX}_z"

        self.LINE_ORIGIN_NAME_SUFFIX = "origin"
        self.LINE_ORIGIN_X_NAME = f"{self.LINE_CENTER_X_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"
        self.LINE_ORIGIN_Y_NAME = f"{self.LINE_CENTER_Y_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"
        self.LINE_ORIGIN_Z_NAME = f"{self.LINE_CENTER_Z_LABEL_PREFIX}_{self.LINE_ORIGIN_NAME_SUFFIX}"
        self.LINE_ORIGIN_X_LABEL = self.LINE_ORIGIN_X_NAME
        self.LINE_ORIGIN_Y_LABEL = self.LINE_ORIGIN_Y_NAME
        self.LINE_ORIGIN_Z_LABEL = self.LINE_ORIGIN_Z_NAME

        self.AXES_MARKER_LINE_LENGTH = 500

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{__title__} v{__version__}")

        self.ui.lbldX.setToolTip("Total translation along the x axis.")
        self.ui.lbldY.setToolTip("Total translation along the y axis.")
        self.ui.lbldZ.setToolTip("Total translation along the z axis.")
        self.ui.lblStep.setToolTip("Step size along any axis.")
        self.ui.lblSnap.setToolTip("Snapping distance for any axis.")
        self.ui.lblTransparency.setToolTip("Transparency value to use for all objects.")

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
        self.ui.btnTransparencyEnable.clicked.connect(self.btnTransparencyEnableClicked)
        self.ui.btnTransparencyDisable.clicked.connect(self.btnTransparencyDisableClicked)

        self.ui.sldTranslateX.valueChanged.connect(self.sldTranslateXChanged)
        self.ui.sldTranslateY.valueChanged.connect(self.sldTranslateYChanged)
        self.ui.sldTranslateZ.valueChanged.connect(self.sldTranslateZChanged)
        self.ui.sldTranslateDelta.valueChanged.connect(self.sldTranslateDeltaChanged)
        self.ui.sldSnapDistance.valueChanged.connect(self.sldSnapDistanceChanged)
        self.ui.sldTransparency.valueChanged.connect(self.sldTransparencyValueChanged)

        self.ui.sldTranslateX.sliderPressed.connect(self.sldPressed)
        self.ui.sldTranslateY.sliderPressed.connect(self.sldPressed)
        self.ui.sldTranslateZ.sliderPressed.connect(self.sldPressed)

        self.ui.sldTranslateX.sliderReleased.connect(self.sldReleased)
        self.ui.sldTranslateY.sliderReleased.connect(self.sldReleased)
        self.ui.sldTranslateZ.sliderReleased.connect(self.sldReleased)

        self.ui.chkAlwaysOnTop.clicked.connect(self.chkAlwaysOnTopClicked)

        self.transformActive = False

        self.centerLines: list = []

        self.axisXTranslation = self.axisYTranslation = self.axisZTranslation = 0

        self.deltaTranslation = float(10 ** self.ui.sldTranslateDelta.value())
        self.snapDistance = float(10 ** self.ui.sldSnapDistance.value())

        # Synchronize the labels.
        self.sldTranslateDeltaChanged()
        self.ui.sldSnapDistance.setValue(1)
        self.sldTransparencyValueChanged()

        self.markerLineColor = (150 / 255.0, 150 / 255.0, 150 / 255.0, 0.0)
        self.markerLineWidth = 2

        self.snapLineColor = (0.0, 1.0, 1.0, 0.0)
        self.snapLineWidth = 4

        self.highlightLineColor = (1.0, 0.0, 0.0, 0.0)

        self.chkAlwaysOnTopClicked()
# ==================================================================================================
    def chkAlwaysOnTopClicked(self) -> None:

        try:
            flags = self.windowFlags()

            if self.ui.chkAlwaysOnTop.isChecked():
                self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(flags & (~Qt.WindowStaysOnTopHint))

            self.show()
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldTranslateXChanged(self) -> None:

        try:
            self.translateSelection(self.ui.sldTranslateX.value(), 0, 0)
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldTranslateYChanged(self) -> None:

        try:
            self.translateSelection(0, self.ui.sldTranslateY.value(), 0)
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldTranslateZChanged(self) -> None:

        try:
            self.translateSelection(0, 0, self.ui.sldTranslateZ.value())
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldTranslateDeltaChanged(self) -> None:

        try:
            self.deltaTranslation = float(10 ** self.ui.sldTranslateDelta.value())
            self.updateTranslationLabels()
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldSnapDistanceChanged(self) -> None:

        try:
            self.snapDistance = float(10 ** self.ui.sldSnapDistance.value())
            self.updateTranslationLabels()
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldTransparencyValueChanged(self) -> None:

        try:
            transparency = self.ui.sldTransparency.value()
            self.ui.lblTransparency2.setText(f"{transparency:g}")
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def getObjectsParameters(self, objects):

        objsParams = [ObjectParameters(obj,
                                       obj.Placement.Base,
                                       self.getCenter(obj),
                                       obj.ViewObject.LineColor if hasattr(obj.ViewObject, "LineColor") else None,
                                       obj.ViewObject.LineWidth if hasattr(obj.ViewObject, "LineWidth") else None,
                                       obj.ViewObject.BoundingBox if hasattr(obj.ViewObject, "BoundingBox") else None)
                      for obj in objects]

        return objsParams
# ==================================================================================================
    def getSelectedObjects(self, extended=False) -> list[ObjectParameters]:

        if extended:
            objs2 = FreeCADGui.Selection.getSelectionEx()
        else:
            objs2 = FreeCADGui.Selection.getSelection()

        objs = []

        for obj in objs2:
            # FreeCAD.Console.PrintMessage(f"Type ID: \"{obj.TypeId}\".\n")

            if extended:
                obj = obj.Object

            if obj.TypeId == "App::DocumentObjectGroup":
                for subObj in obj.Group:
                    try:
                        if hasattr(subObj, "Placement"):
                            objs.append(subObj)
                        else:
                            FreeCAD.Console.PrintMessage(f"Not selecting \"{subObj.Label}\".\n")
                    except:
                        FreeCAD.Console.PrintMessage(f"Exception; cannot select \"{subObj.Label}\".\n")
            else:
                if hasattr(obj, "Placement"):
                    objs.append(obj)
                else:
                    FreeCAD.Console.PrintMessage(f"Not selecting \"{obj.Label}\".\n")

        selObjs = self.getObjectsParameters(objs)

        return selObjs
# ==================================================================================================
    def sldPressed(self) -> None:

        try:
            FreeCAD.ActiveDocument.openTransaction()

            self.centerLines = []

            self.selectedObjsParams = self.getSelectedObjects(extended=True)

            objs = self.getSelectedObjects(extended=False)

            for obj in objs:
                if obj not in self.selectedObjsParams:
                    self.selectedObjsParams.append(obj)

            for objParams in self.selectedObjsParams:
                if self.ui.chkBoundingBoxes.isChecked() and objParams.boundingBoxEnabled is not None:
                    objParams.object.ViewObject.BoundingBox = True

                if self.ui.chkHighlight.isChecked() and objParams.lineColor is not None:
                    objParams.object.ViewObject.LineColor = self.highlightLineColor

            self.snapLinesParams = self.getGroupObjects(self.GROUP_LABEL_CENTER_LINES)
            self.snapLinesParams += self.getGroupObjects(self.GROUP_LABEL_ORIGIN_LINES)
            self.snapLinesParams += self.getGroupObjects(self.GROUP_LABEL_GRID_LINES)

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
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def drawCenterMarks(self, dx, dy, dz, add) -> None:

        for i, objParams in enumerate(self.selectedObjsParams):
            lines = self.drawCenterMark(i, self.getCenter(objParams.object), (dx, dy, dz), "", add)
            if add:
                self.centerLines.append(lines)
                self.addToGroup(lines, self.GROUP_LABEL_TEMP_CENTER_LINES)
# ==================================================================================================
    def drawCenterMark(self, i, p1, offset, objectLabel, add) -> list:
        """
        Draw and move center marks.
        """

        dx = offset[0]
        dy = offset[1]
        dz = offset[2]

        p2 = FreeCAD.Vector(self.AXES_MARKER_LINE_LENGTH, 0, 0)
        p3 = FreeCAD.Vector(0, self.AXES_MARKER_LINE_LENGTH, 0)
        p4 = FreeCAD.Vector(0, 0, self.AXES_MARKER_LINE_LENGTH)

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
                line = FreeCAD.ActiveDocument.addObject("Part::Line", self.LINE_CENTER_NAME_PREFIX)
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
            l1 = FreeCAD.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_X_NAME)
            l1.Label = self.LINE_ORIGIN_X_LABEL
            l1.X1 = -self.AXES_MARKER_LINE_LENGTH
            l1.X2 = self.AXES_MARKER_LINE_LENGTH
            l1.Y1 = l1.Z1 = l1.Y2 = l1.Z2 = 0

            l2 = FreeCAD.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_Y_NAME)
            l2.Label = self.LINE_ORIGIN_Y_LABEL
            l2.Y1 = -self.AXES_MARKER_LINE_LENGTH
            l2.Y2 = self.AXES_MARKER_LINE_LENGTH
            l2.X1 = l2.Z1 = l2.X2 = l2.Z2 = 0

            l3 = FreeCAD.ActiveDocument.addObject("Part::Line", self.LINE_ORIGIN_Z_NAME)
            l3.Label = self.LINE_ORIGIN_Z_LABEL
            l3.Z1 = -self.AXES_MARKER_LINE_LENGTH
            l3.Z2 = self.AXES_MARKER_LINE_LENGTH
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
            obj.ViewObject.Selectable = False
            obj.ViewObject.LineWidth = self.markerLineWidth

            if obj.Label == self.LINE_ORIGIN_X_LABEL:
                obj.ViewObject.LineColor = (1.0, 0.0, 0.0, 0.0)
            elif obj.Label == self.LINE_ORIGIN_Y_LABEL:
                obj.ViewObject.LineColor = (0.0, 1.0, 0.0, 0.0)
            elif obj.Label == self.LINE_ORIGIN_Z_LABEL:
                obj.ViewObject.LineColor = (0.0, 0.0, 1.0, 0.0)
# ==================================================================================================
    def getGroup(self, groupLabel, autoCreate):

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
# ==================================================================================================
    def removeGroup(self, groupLabel) -> None:

        objsParams = self.getGroupObjects(groupLabel)

        for objParams in objsParams:
            self.removeObject(objParams.object)

        self.removeObjectsByLabel(groupLabel)
# ==================================================================================================
    def addToGroup(self, objs: tuple[Any] | list[Any], groupLabel: str) -> None:

        group = self.getGroup(groupLabel, True)
        assert group

        for obj in objs:
            group.addObject(obj)
# ==================================================================================================
    def getGroupObjects(self, groupLabel) -> list[ObjectParameters]:

        group = self.getGroup(groupLabel, False)

        if group is None:
            return []

        objs = []

        for obj in group.Group:
            if type(obj.Shape) is not Part.Face:
                objs.append(obj)
            else:
                FreeCAD.Console.PrintMessage(f"Not selecting \"{obj.Label}\".\n")

        groupObjs = self.getObjectsParameters(objs)

        return groupObjs
# ==================================================================================================
    def btnAddCenterMarkClicked(self) -> None:

        try:
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
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnToggleOriginMarkClicked(self) -> None:

        try:
            group = self.getGroup(self.GROUP_LABEL_ORIGIN_LINES, False)

            if group == None:
                self.addRemoveOriginMark(True)
            else:
                self.addRemoveOriginMark(False)
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def sldReleased(self) -> None:

        try:
            prevTransform = self.transformActive

            # Transformation has ended.
            self.transformActive = False

            self.ui.sldTranslateX.setValue(0)
            self.ui.sldTranslateY.setValue(0)
            self.ui.sldTranslateZ.setValue(0)

            self.updateTranslationLabels()

            if not prevTransform:
                return

            for objParams in self.selectedObjsParams:
                if self.ui.chkBoundingBoxes.isChecked() and objParams.boundingBoxEnabled is not None:
                    # Restore the status of bounding boxes.
                    objParams.object.ViewObject.BoundingBox = objParams.boundingBoxEnabled

                if self.ui.chkHighlight.isChecked() and objParams.lineColor is not None:
                    # Restore the line colors.
                    objParams.object.ViewObject.LineColor = objParams.lineColor

            if self.drawStyleRevertAction is not None:
                self.drawStyleRevertAction.trigger()

            self.removeGroup(self.GROUP_LABEL_TEMP_CENTER_LINES)
            self.clearSnapHighlighting()

            if self.ui.chkAutoRecompute.isChecked():
                FreeCAD.ActiveDocument.recompute()

            FreeCAD.ActiveDocument.commitTransaction()

            self.ui.statusBar.clearMessage()
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnResetTransformsClicked(self) -> None:

        try:
            self.selectedObjsParams = self.getSelectedObjects(extended=False)

            if len(self.selectedObjsParams) == 0:
                return

            self.ui.statusBar.clearMessage()

            FreeCAD.ActiveDocument.openTransaction()

            for objParam in self.selectedObjsParams:
                objParam.object.Placement = \
                    FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                                      FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0))

            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def updateTranslationLabels(self) -> None:

        self.ui.lblTranslateX.setText(f"{self.axisXTranslation:g}")
        self.ui.lblTranslateY.setText(f"{self.axisYTranslation:g}")
        self.ui.lblTranslateZ.setText(f"{self.axisZTranslation:g}")
        self.ui.lblTranslateDelta.setText(f"{self.deltaTranslation:g}")
        self.ui.lblSnapDistance.setText(f"{self.snapDistance:g}")
# ==================================================================================================
    def translateSelection(self, x, y, z) -> None:

        if len(self.selectedObjsParams) == 0:
            self.ui.statusBar.showMessage("Nothing selected.")
            return

        if len(self.selectedObjsParams) == 1:
            objLabel = self.selectedObjsParams[0].object.Label
            self.ui.statusBar.showMessage(f"Translating \"{objLabel}\".")
        else:
            objsCount = len(self.selectedObjsParams)
            self.ui.statusBar.showMessage(f"Translating {objsCount} objects.")

        if not self.transformActive:
            self.ui.sldTranslateX.setValue(0)
            self.ui.sldTranslateY.setValue(0)
            self.ui.sldTranslateZ.setValue(0)

            self.axisXTranslation = self.axisYTranslation = self.axisZTranslation = 0
            self.updateTranslationLabels()
            return

        for objParams in self.selectedObjsParams:
            self.axisXTranslation = x * self.deltaTranslation
            self.axisYTranslation = y * self.deltaTranslation
            self.axisZTranslation = z * self.deltaTranslation

            if self.ui.chkSnap.isChecked():
                self.checkSnapping()

            # Use the base as a reference before moving started (updated when the slider is released).
            base = objParams.base

            newX = base.x + self.axisXTranslation
            newY = base.y + self.axisYTranslation
            newZ = base.z + self.axisZTranslation

            newBase = FreeCAD.Vector(newX, newY, newZ)

            obj = objParams.object
            obj.Placement.Base = newBase

            if self.ui.chkAutoUpdateView.isChecked():
                obj.ViewObject.update()

            if self.ui.chkCenterMarks.isChecked():
                self.drawCenterMarks(0, 0, 0, False)

            self.updateTranslationLabels()
# ==================================================================================================
    def clearSnapHighlighting(self) -> None:
        """
        Clear snapping related highlighting.
        """

        for snapLineParams in self.snapLinesParams:
            viewObject = snapLineParams.object.ViewObject
            viewObject.LineColor = snapLineParams.lineColor
            viewObject.LineWidth = snapLineParams.lineWidth
# ==================================================================================================
    def checkSnapping(self) -> None:

        self.clearSnapHighlighting()

        if (self.axisXTranslation == 0) and (self.axisYTranslation == 0) and (self.axisZTranslation == 0):
            return

        linePrefixes = {}

        linePrefixes["x"] = [self.LINE_CENTER_Y_LABEL_PREFIX,
                             self.LINE_CENTER_Z_LABEL_PREFIX,
                             self.LINE_GRID_Y_LABEL_PREFIX,
                             self.LINE_GRID_Z_LABEL_PREFIX]

        linePrefixes["y"] = [self.LINE_CENTER_X_LABEL_PREFIX,
                             self.LINE_CENTER_Z_LABEL_PREFIX,
                             self.LINE_GRID_X_LABEL_PREFIX,
                             self.LINE_GRID_Z_LABEL_PREFIX]

        linePrefixes["z"] = [self.LINE_CENTER_X_LABEL_PREFIX,
                             self.LINE_CENTER_Y_LABEL_PREFIX,
                             self.LINE_GRID_X_LABEL_PREFIX,
                             self.LINE_GRID_Y_LABEL_PREFIX]

        for objParams in self.selectedObjsParams:
            # Use the center as a reference before moving starts.
            # The center is updated when the slider is released.
            center = objParams.center

            newCenterX = center[0] + self.axisXTranslation
            newCenterY = center[1] + self.axisYTranslation
            newCenterZ = center[2] + self.axisZTranslation

            snapped = False
            objSnapLine = None
            lblSnapLine = None
            axis = None
            diff = 0

            for snapLine in self.snapLinesParams:
                objSnapLine = snapLine.object
                lblSnapLine = objSnapLine.Label

                if (self.axisXTranslation != 0) and (objSnapLine.X1 == objSnapLine.X2):
                    axis = "x"
                    diff = float(objSnapLine.X1) - newCenterX

                elif (self.axisYTranslation != 0) and (objSnapLine.Y1 == objSnapLine.Y2):
                    axis = "y"
                    diff = float(objSnapLine.Y1) - newCenterY

                elif (self.axisZTranslation != 0) and (objSnapLine.Z1 == objSnapLine.Z2):
                    axis = "z"
                    diff = float(objSnapLine.Z1) - newCenterZ

                else:
                    continue

                for linePrefix in linePrefixes[axis]:
                    if lblSnapLine.startswith(linePrefix):
                        if abs(diff) <= self.snapDistance:
                            snapped = True
                            break

                if snapped:
                    break

            if snapped:
                assert objSnapLine
                assert lblSnapLine
                assert axis

                objSnapLine.ViewObject.LineColor = self.snapLineColor
                objSnapLine.ViewObject.LineWidth = self.snapLineWidth

                if axis == "x":
                    self.axisXTranslation += diff
                elif axis == "y":
                    self.axisYTranslation += diff
                elif axis == "z":
                    self.axisZTranslation += diff

                message = f"\"{objParams.object.Label}\" snapped to reference line \"{lblSnapLine}\"."
                self.ui.statusBar.showMessage(message)

                break
# ==================================================================================================
    def btnOrthographicClicked(self) -> None:

        try:
            self.ui.statusBar.clearMessage()
            Gui.activeDocument().activeView().setCameraType("Orthographic")
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnPerspectiveClicked(self) -> None:

        try:
            self.ui.statusBar.clearMessage()
            Gui.activeDocument().activeView().setCameraType("Perspective")
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnDefaultLineColorClicked(self) -> None:

        try:
            self.ui.statusBar.clearMessage()

            r = self.markerLineColor[0] * 255
            g = self.markerLineColor[1] * 255
            b = self.markerLineColor[2] * 255

            color = QColorDialog.getColor(QColor(r, g, b), None)

            if color.isValid():
                r = color.red()
                g = color.green()
                b = color.blue()

                self.markerLineColor = (r / 255.0, g / 255.0, b / 255.0, 0.0)
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnTransparencyEnableClicked(self):

        try:
            self.setTransparencies(self.ui.sldTransparency.value())
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def btnTransparencyDisableClicked(self):

        try:
            self.setTransparencies(0)
        except:
            QMessageBox.critical(self, "Exception", format_exc())
# ==================================================================================================
    def setTransparencies(self, value):

        for obj in FreeCAD.ActiveDocument.Objects:
            viewObject = obj.ViewObject

            if hasattr(viewObject, "Transparency"):
                viewObject.Transparency = value
# ==================================================================================================
    def removeObject(self, obj) -> None:

        FreeCAD.ActiveDocument.removeObject(obj.Name)
# ==================================================================================================
    def removeObjects(self, objs) -> None:

        for obj in objs:
            self.removeObject(obj)
# ==================================================================================================
    def removeObjectsByLabel(self, label) -> None:

        objs = FreeCAD.ActiveDocument.getObjectsByLabel(label)

        for obj in objs:
            self.removeObject(obj)
# ==================================================================================================
    # def isOriginLine(self, obj):

    #     return obj.Label in [self.LINE_ORIGIN_X_NAME, self.LINE_ORIGIN_Y_NAME, self.LINE_ORIGIN_Z_NAME]
# ==================================================================================================
    # def isCenterLine(self, obj):

    #     return obj.Label.startswith(self.LINE_CENTER_NAME_PREFIX)
# ==================================================================================================
    def getCenter(self, obj) -> "FreeCAD.Vector":

        center = None

        if hasattr(obj, "Shape"):
            center = obj.Shape.BoundBox.Center
        elif hasattr(obj, "Mesh"):
            center = obj.Mesh.BoundBox.Center
        elif hasattr(obj, "Placement"):
            center = obj.Placement.Base

        return center
# ===========================================================================
    def getAllCenters(self) -> list["FreeCAD.Vector"]:

        centers: list["FreeCAD.Vector"] = []

        for objParams in self.selectedObjsParams:
            centers.append(self.getCenter(objParams.object))

        return centers
# ===========================================================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(460, 430)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(460, 430))
        MainWindow.setMaximumSize(QSize(460, 430))
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
        self.sldTranslateX = QSlider(self.tab)
        self.sldTranslateX.setObjectName(u"sldTranslateX")
        self.sldTranslateX.setGeometry(QRect(50, 0, 300, 40))
        self.sldTranslateX.setMinimum(-50)
        self.sldTranslateX.setMaximum(50)
        self.sldTranslateX.setPageStep(1)
        self.sldTranslateX.setOrientation(Qt.Horizontal)
        self.sldTranslateY = QSlider(self.tab)
        self.sldTranslateY.setObjectName(u"sldTranslateY")
        self.sldTranslateY.setGeometry(QRect(50, 30, 300, 40))
        self.sldTranslateY.setMinimum(-50)
        self.sldTranslateY.setMaximum(50)
        self.sldTranslateY.setPageStep(1)
        self.sldTranslateY.setOrientation(Qt.Horizontal)
        self.sldTranslateZ = QSlider(self.tab)
        self.sldTranslateZ.setObjectName(u"sldTranslateZ")
        self.sldTranslateZ.setGeometry(QRect(50, 60, 300, 40))
        self.sldTranslateZ.setMinimum(-50)
        self.sldTranslateZ.setMaximum(50)
        self.sldTranslateZ.setPageStep(1)
        self.sldTranslateZ.setOrientation(Qt.Horizontal)
        self.sldTranslateDelta = QSlider(self.tab)
        self.sldTranslateDelta.setObjectName(u"sldTranslateDelta")
        self.sldTranslateDelta.setGeometry(QRect(50, 90, 300, 40))
        self.sldTranslateDelta.setMinimum(-9)
        self.sldTranslateDelta.setMaximum(9)
        self.sldTranslateDelta.setPageStep(1)
        self.sldTranslateDelta.setOrientation(Qt.Horizontal)
        self.chkWireFrame = QCheckBox(self.tab)
        self.chkWireFrame.setObjectName(u"chkWireFrame")
        self.chkWireFrame.setGeometry(QRect(10, 290, 180, 30))
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
        self.lblTranslateX.setGeometry(QRect(360, 10, 100, 20))
        self.lblTranslateX.setAlignment(Qt.AlignCenter)
        self.lblTranslateZ = QLabel(self.tab)
        self.lblTranslateZ.setObjectName(u"lblTranslateZ")
        self.lblTranslateZ.setGeometry(QRect(360, 70, 100, 20))
        self.lblTranslateZ.setAlignment(Qt.AlignCenter)
        self.lblTranslateY = QLabel(self.tab)
        self.lblTranslateY.setObjectName(u"lblTranslateY")
        self.lblTranslateY.setGeometry(QRect(360, 40, 100, 20))
        self.lblTranslateY.setAlignment(Qt.AlignCenter)
        self.lblTranslateDelta = QLabel(self.tab)
        self.lblTranslateDelta.setObjectName(u"lblTranslateDelta")
        self.lblTranslateDelta.setGeometry(QRect(360, 100, 100, 20))
        self.lblTranslateDelta.setAlignment(Qt.AlignCenter)
        self.btnOrthographic = QPushButton(self.tab)
        self.btnOrthographic.setObjectName(u"btnOrthographic")
        self.btnOrthographic.setEnabled(True)
        self.btnOrthographic.setGeometry(QRect(10, 160, 140, 40))
        self.btnOrthographic.setMinimumSize(QSize(0, 0))
        self.btnPerspective = QPushButton(self.tab)
        self.btnPerspective.setObjectName(u"btnPerspective")
        self.btnPerspective.setEnabled(True)
        self.btnPerspective.setGeometry(QRect(10, 210, 140, 40))
        self.btnPerspective.setMinimumSize(QSize(0, 0))
        self.btnAddCenterMark = QPushButton(self.tab)
        self.btnAddCenterMark.setObjectName(u"btnAddCenterMark")
        self.btnAddCenterMark.setEnabled(True)
        self.btnAddCenterMark.setGeometry(QRect(160, 160, 140, 40))
        self.btnAddCenterMark.setMinimumSize(QSize(0, 0))
        self.chkSnap = QCheckBox(self.tab)
        self.chkSnap.setObjectName(u"chkSnap")
        self.chkSnap.setGeometry(QRect(10, 320, 180, 30))
        self.btnDefaultLineColor = QPushButton(self.tab)
        self.btnDefaultLineColor.setObjectName(u"btnDefaultLineColor")
        self.btnDefaultLineColor.setEnabled(True)
        self.btnDefaultLineColor.setGeometry(QRect(310, 210, 140, 40))
        self.btnDefaultLineColor.setMinimumSize(QSize(0, 0))
        self.chkCenterMarks = QCheckBox(self.tab)
        self.chkCenterMarks.setObjectName(u"chkCenterMarks")
        self.chkCenterMarks.setGeometry(QRect(160, 290, 200, 30))
        self.chkAutoUpdateView = QCheckBox(self.tab)
        self.chkAutoUpdateView.setObjectName(u"chkAutoUpdateView")
        self.chkAutoUpdateView.setGeometry(QRect(10, 350, 180, 30))
        self.chkAutoRecompute = QCheckBox(self.tab)
        self.chkAutoRecompute.setObjectName(u"chkAutoRecompute")
        self.chkAutoRecompute.setGeometry(QRect(160, 350, 200, 30))
        self.chkAutoRecompute.setChecked(True)
        self.sldSnapDistance = QSlider(self.tab)
        self.sldSnapDistance.setObjectName(u"sldSnapDistance")
        self.sldSnapDistance.setGeometry(QRect(50, 120, 300, 40))
        self.sldSnapDistance.setMinimum(-9)
        self.sldSnapDistance.setMaximum(9)
        self.sldSnapDistance.setPageStep(1)
        self.sldSnapDistance.setOrientation(Qt.Horizontal)
        self.lblSnapDistance = QLabel(self.tab)
        self.lblSnapDistance.setObjectName(u"lblSnapDistance")
        self.lblSnapDistance.setGeometry(QRect(360, 130, 100, 20))
        self.lblSnapDistance.setAlignment(Qt.AlignCenter)
        self.lblSnap = QLabel(self.tab)
        self.lblSnap.setObjectName(u"lblSnap")
        self.lblSnap.setGeometry(QRect(10, 130, 40, 20))
        self.chkBoundingBoxes = QCheckBox(self.tab)
        self.chkBoundingBoxes.setObjectName(u"chkBoundingBoxes")
        self.chkBoundingBoxes.setGeometry(QRect(160, 260, 200, 30))
        self.chkAlwaysOnTop = QCheckBox(self.tab)
        self.chkAlwaysOnTop.setObjectName(u"chkAlwaysOnTop")
        self.chkAlwaysOnTop.setGeometry(QRect(10, 260, 180, 30))
        self.btnToggleOriginMark = QPushButton(self.tab)
        self.btnToggleOriginMark.setObjectName(u"btnToggleOriginMark")
        self.btnToggleOriginMark.setEnabled(True)
        self.btnToggleOriginMark.setGeometry(QRect(160, 210, 140, 40))
        self.btnToggleOriginMark.setMinimumSize(QSize(0, 0))
        self.chkHighlight = QCheckBox(self.tab)
        self.chkHighlight.setObjectName(u"chkHighlight")
        self.chkHighlight.setGeometry(QRect(160, 320, 200, 30))
        self.chkHighlight.setChecked(True)
        self.tabMain.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.lblTransparency2 = QLabel(self.tab_2)
        self.lblTransparency2.setObjectName(u"lblTransparency2")
        self.lblTransparency2.setGeometry(QRect(360, 40, 100, 20))
        self.lblTransparency2.setAlignment(Qt.AlignCenter)
        self.lblTransparency = QLabel(self.tab_2)
        self.lblTransparency.setObjectName(u"lblTransparency")
        self.lblTransparency.setGeometry(QRect(10, 40, 40, 20))
        self.sldTransparency = QSlider(self.tab_2)
        self.sldTransparency.setObjectName(u"sldTransparency")
        self.sldTransparency.setGeometry(QRect(50, 30, 300, 40))
        self.sldTransparency.setMinimum(0)
        self.sldTransparency.setMaximum(100)
        self.sldTransparency.setSingleStep(5)
        self.sldTransparency.setPageStep(5)
        self.sldTransparency.setValue(50)
        self.sldTransparency.setOrientation(Qt.Horizontal)
        self.btnTransparencyEnable = QPushButton(self.tab_2)
        self.btnTransparencyEnable.setObjectName(u"btnTransparencyEnable")
        self.btnTransparencyEnable.setEnabled(True)
        self.btnTransparencyEnable.setGeometry(QRect(160, 70, 140, 40))
        self.btnTransparencyEnable.setMinimumSize(QSize(0, 0))
        self.btnTransparencyDisable = QPushButton(self.tab_2)
        self.btnTransparencyDisable.setObjectName(u"btnTransparencyDisable")
        self.btnTransparencyDisable.setEnabled(True)
        self.btnTransparencyDisable.setGeometry(QRect(160, 120, 140, 40))
        self.btnTransparencyDisable.setMinimumSize(QSize(0, 0))
        self.lblTransparency_2 = QLabel(self.tab_2)
        self.lblTransparency_2.setObjectName(u"lblTransparency_2")
        self.lblTransparency_2.setGeometry(QRect(10, 10, 250, 20))
        self.tabMain.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        QWidget.setTabOrder(self.sldTranslateX, self.sldTranslateY)
        QWidget.setTabOrder(self.sldTranslateY, self.sldTranslateZ)
        QWidget.setTabOrder(self.sldTranslateZ, self.sldTranslateDelta)
        QWidget.setTabOrder(self.sldTranslateDelta, self.btnResetTransforms)
        QWidget.setTabOrder(self.btnResetTransforms, self.btnAddCenterMark)
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
        self.btnToggleOriginMark.setText(QCoreApplication.translate("MainWindow", u"Toggle Origin Mark", None))
        self.chkHighlight.setText(QCoreApplication.translate("MainWindow", u"Highlight when moving", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab),
                                QCoreApplication.translate("MainWindow", u"Transform", None))
        self.lblTransparency2.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.lblTransparency.setText(QCoreApplication.translate("MainWindow", u"Tran", None))
        self.btnTransparencyEnable.setText(QCoreApplication.translate("MainWindow", u"Enable/Apply", None))
        self.btnTransparencyDisable.setText(QCoreApplication.translate("MainWindow", u"Disable", None))
        self.lblTransparency_2.setText(QCoreApplication.translate(
            "MainWindow", u"Set transparency of all objects:", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab_2),
                                QCoreApplication.translate("MainWindow", u"View", None))
# ===========================================================================
macroWindow = MacroWindow(FreeCADGui.getMainWindow())
# ===========================================================================
