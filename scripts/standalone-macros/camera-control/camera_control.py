"""
***************************************************************************
*                                                                         *
*   Author:  Naveed Alam                                                  *
*   Email:   naveedguy ayt gmail dot com                                  *
*   Source:  https://github.com/nvdl/FreeCAD                              *
*   License: https://github.com/FreeCAD/FreeCAD/blob/main/LICENSE         *
*                                                                         *
***************************************************************************
*                                                                         *
*   This macro allows for precise positioning of the camera.              *
*                                                                         *
*   It supports:                                                          *
*   - Camera's translation.                                               *
*   - Camera's rotation.                                                  *
*   - Camera's field (angle) of view (FOV).                               *
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
"""
# ==================================================================================================
import math

import FreeCAD
import FreeCADGui
from PySide.QtCore import QCoreApplication, QEvent, QMetaObject, QRect, QSize, Qt
from PySide.QtGui import QAction, QKeyEvent

from PySide.QtWidgets import (
    QCheckBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QTabWidget,
    QWidget,
)
# ==================================================================================================
__title__ = "CameraControl"
__version__ = "2.0"
__date__ = "26/09/2026"
__author__ = "Naveed Alam"
__Requires__ = "Freecad 1.1.0"
__Status__ = "stable"
__Comment__ = "This macro allows for precise positioning of the camera using the keyboard."
__url__ = "http://www.freecadweb.org/"
__Web__ = "http://www.freecadweb.org/"
__Wiki__ = "http://www.freecadweb.org/wiki/"
__License__ = "LGPL-2.0-or-later"
__Icon__ = ""
__IconW__ = ""
__Help__ = ""
# ==================================================================================================
class MacroWindow(QMainWindow):

    def __init__(self, parent=None) -> None:

        self.consumeKeys = (
            Qt.Key.Key_W,
            Qt.Key.Key_S,
            Qt.Key.Key_A,
            Qt.Key.Key_D,
            Qt.Key.Key_E,
            Qt.Key.Key_Q,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down
        )

        self.keysMap = {
            Qt.Key.Key_W: "forward",
            Qt.Key.Key_S: "backward",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_D: "right",
            Qt.Key.Key_E: "up",
            Qt.Key.Key_Q: "down",
            Qt.Key.Key_Left: "rotate-left",
            Qt.Key.Key_Right: "rotate-right",
            Qt.Key.Key_Up: "rotate-up",
            Qt.Key.Key_Down: "rotate-down"
        }

        # Default field-of-view angle.
        self.DEFAULT_FOV = 45

        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{__title__} v{__version__}")

        self.ui.sldTranslateDelta.valueChanged.connect(self.sldTranslateDeltaChanged)
        self.ui.sldTranslateDelta.installEventFilter(self)

        self.ui.sldHeightAngle.valueChanged.connect(self.sldHeightAngleChanged)
        self.ui.sldHeightAngle.installEventFilter(self)
        self.ui.sldHeightAngle.setValue(self.DEFAULT_FOV)

        self.deltaTranslation = float(2 ** self.ui.sldTranslateDelta.value())
        self.heightAngle = self.ui.sldHeightAngle.value()

        self.ui.btnForward.clicked.connect(self.btnForwardClicked)
        self.ui.btnBackward.clicked.connect(self.btnBackwardClicked)
        self.ui.btnLeft.clicked.connect(self.btnLeftClicked)
        self.ui.btnRight.clicked.connect(self.btnRightClicked)
        self.ui.btnUp.clicked.connect(self.btnUpClicked)
        self.ui.btnDown.clicked.connect(self.btnDownClicked)

        self.ui.btnRotLeft.clicked.connect(self.btnRotLeftClicked)
        self.ui.btnRotRight.clicked.connect(self.btnRotRightClicked)
        self.ui.btnRotUp.clicked.connect(self.btnRotUpClicked)
        self.ui.btnRotDown.clicked.connect(self.btnRotDownClicked)

        self.setStyleSheet("""
            QPushButton {
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                padding: 0px 0px;
            }
        """)

        # Synchronize the labels.
        self.sldTranslateDeltaChanged()
        self.sldHeightAngleChanged()

        self.alwaysOnTop(True)
# ==================================================================================================
    def alwaysOnTop(self, status) -> None:

        flags = self.windowFlags()

        if status:
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & (~Qt.WindowType.WindowStaysOnTopHint))

        self.show()
# ==================================================================================================
    def eventFilter(self, obj, event) -> bool:

        # Consume the event.
        return obj in (self.ui.sldTranslateDelta, self.ui.sldHeightAngle) and \
            (event.type() is QEvent.Type.KeyPress) and (event.key() in self.consumeKeys)
# ==================================================================================================
    def keyReleaseEvent(self, event: QKeyEvent) -> None:

        key = event.key()

        if key in self.keysMap:
            if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                self.rotateCamera(self.keysMap[key])
            else:
                self.translateCamera(self.keysMap[key])

        super().keyReleaseEvent(event)
# ==================================================================================================
    def btnForwardClicked(self) -> None:

        self.translateCamera("forward")
# ==================================================================================================
    def btnBackwardClicked(self) -> None:

        self.translateCamera("backward")
# ==================================================================================================
    def btnLeftClicked(self) -> None:

        self.translateCamera("left")
# ==================================================================================================
    def btnRightClicked(self) -> None:

        self.translateCamera("right")
# ==================================================================================================
    def btnUpClicked(self) -> None:

        self.translateCamera("up")
# ==================================================================================================
    def btnDownClicked(self) -> None:

        self.translateCamera("down")
# ==================================================================================================
    def btnRotLeftClicked(self) -> None:

        self.rotateCamera("rotate-left")
# ==================================================================================================
    def btnRotRightClicked(self) -> None:

        self.rotateCamera("rotate-right")
# ==================================================================================================
    def btnRotUpClicked(self) -> None:

        self.rotateCamera("rotate-up")
# ==================================================================================================
    def btnRotDownClicked(self) -> None:

        self.rotateCamera("rotate-down")
# ==================================================================================================
    def translateCamera(self, direction: str) -> None:

        if not (FreeCADGui.ActiveDocument and FreeCADGui.ActiveDocument.ActiveView):
            return

        camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

        if not camera:
            return

        if direction in ("forward", "backward"):
            # Local forward in camera space is (0, 0, –1).
            localDir = FreeCAD.Vector(0, 0, -1)
        elif direction in ("left", "right"):
            # Local left in camera space is (-1, 0, 0).
            localDir = FreeCAD.Vector(-1, 0, 0)
        elif direction in ("up", "down"):
            # Local down in camera space is (0, -1, 0).
            localDir = FreeCAD.Vector(0, -1, 0)
        else:
            return

        # Convert orientation quaternion to "FreeCAD.Rotation".
        qTuple = camera.orientation.getValue().getValue()
        cameraDir = FreeCAD.Rotation(*qTuple)

        if self.ui.chkXYRestricted.isChecked():
            # FreeCAD uses Yaw (around Z), Pitch (around X), Roll (around Y).
            # Angles are in degrees.
            yaw, pitch, roll = cameraDir.getYawPitchRoll()

            roll = 90
            cameraDir = FreeCAD.Rotation(yaw, pitch, roll)

        # Transform camera space to world space and normalize.
        worldDir = cameraDir.multVec(localDir).normalize()

        # Invert vector direction for opposite movements.
        if direction in ("backward", "right", "up"):
            worldDir = -worldDir

        # Calculate translation step.
        translation = worldDir * self.deltaTranslation

        # Update camera's position.
        posTuple = camera.position.getValue().getValue()
        currentPosition = FreeCAD.Vector(*posTuple)
        newPosition = currentPosition + translation

        camera.position.setValue(newPosition)

        if hasattr(camera, "heightAngle"):
            camera.heightAngle.setValue(math.radians(self.heightAngle))

        self.updateInfo(camera)
# ==================================================================================================
    def rotateCamera(self, direction: str) -> None:

        if not (FreeCADGui.ActiveDocument and FreeCADGui.ActiveDocument.ActiveView):
            return

        camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

        if not camera:
            return

        step = self.deltaTranslation

        directionRot = direction.split("-")[1]
        angleDegrees = step if directionRot in ("left", "up") else -step

        axis = "roll" if directionRot in ("left", "right") else "pitch"

        # Ignore orientation of the camera when rotating left or right.
        # Rotate around the global Z-axis.
        useGlobal = (axis == "roll")

        qTuple = camera.orientation.getValue().getValue()
        currentRotation = FreeCAD.Rotation(*qTuple)

        # Define the rotation axis.
        if axis == "pitch":
            baseAxis = FreeCAD.Vector(1, 0, 0)
        elif axis == "yaw":
            baseAxis = FreeCAD.Vector(0, 1, 0)
        elif axis == "roll":
            baseAxis = FreeCAD.Vector(0, 0, 1)
        else:
            return

        # Create incremental rotation around the selected axis.
        deltaRotation = FreeCAD.Rotation(baseAxis, angleDegrees)

        if useGlobal:
            # Global space: Apply rotation on the left side of current orientation.
            newRotation = deltaRotation.multiply(currentRotation)
        else:
            # Local space: Apply rotation on the right side in camera body space.
            newRotation = currentRotation.multiply(deltaRotation)

        # Extract quaternion tuple (q0, q1, q2, q3) and assign to the camera node.
        camera.orientation.setValue(newRotation.Q)

        self.updateInfo(camera)
# ==================================================================================================
    def sldTranslateDeltaChanged(self) -> None:

        self.deltaTranslation = float(2 ** self.ui.sldTranslateDelta.value())
        self.ui.lblTranslateDelta.setText(f"Step size: {self.deltaTranslation:g}")
# ==================================================================================================
    def sldHeightAngleChanged(self) -> None:

        self.heightAngle = self.ui.sldHeightAngle.value()
        self.ui.lblHeightAngle.setText(f"FOV: {self.heightAngle:g}")

        if FreeCADGui.ActiveDocument and FreeCADGui.ActiveDocument.ActiveView:
            camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
            if camera and hasattr(camera, "heightAngle"):
                camera.heightAngle.setValue(math.radians(self.heightAngle))
# ==================================================================================================
    def updateInfo(self, camera) -> None:

        cameraPosition = FreeCAD.Vector(camera.position.getValue())
        step = self.deltaTranslation

        cameraPositionX = int(cameraPosition.x / step) * step
        cameraPositionY = int(cameraPosition.y / step) * step
        cameraPositionZ = int(cameraPosition.z / step) * step

        cameraOrientationTuple = camera.orientation.getValue().getValue()

        cameraOrientation = FreeCAD.Rotation(
            cameraOrientationTuple[0],
            cameraOrientationTuple[1],
            cameraOrientationTuple[2],
            cameraOrientationTuple[3]
        )

        cameraOrientationAngle = round(math.degrees(cameraOrientation.Angle), 2)

        self.ui.lblInfo.setText(f"X: {cameraPositionX}\n"
                                f"Y: {cameraPositionY}\n"
                                f"Z: {cameraPositionZ}\n"
                                f"OAngle: {cameraOrientationAngle} deg\n"
                                f"OAxis: {round(cameraOrientation.Axis.x, 2)}, "
                                f"{round(cameraOrientation.Axis.y, 2)}, "
                                f"{round(cameraOrientation.Axis.z, 2)}")
# ==================================================================================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(150, 540)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(150, 450))
        MainWindow.setMaximumSize(QSize(150, 600))
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
        self.tabMain.setGeometry(QRect(0, 0, 150, 541))
        self.tabMain.setIconSize(QSize(16, 16))
        self.tabMain.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabMain.setDocumentMode(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.btnUp = QPushButton(self.tab)
        self.btnUp.setObjectName(u"btnUp")
        self.btnUp.setEnabled(True)
        self.btnUp.setGeometry(QRect(110, 160, 30, 30))
        self.sldTranslateDelta = QSlider(self.tab)
        self.sldTranslateDelta.setObjectName(u"sldTranslateDelta")
        self.sldTranslateDelta.setGeometry(QRect(10, 30, 180, 40))
        self.sldTranslateDelta.setMinimum(-9)
        self.sldTranslateDelta.setMaximum(9)
        self.sldTranslateDelta.setPageStep(1)
        self.sldTranslateDelta.setOrientation(Qt.Orientation.Horizontal)
        self.lblTranslateDelta = QLabel(self.tab)
        self.lblTranslateDelta.setObjectName(u"lblTranslateDelta")
        self.lblTranslateDelta.setGeometry(QRect(10, 10, 140, 20))
        self.btnDown = QPushButton(self.tab)
        self.btnDown.setObjectName(u"btnDown")
        self.btnDown.setEnabled(True)
        self.btnDown.setGeometry(QRect(10, 160, 30, 30))
        self.btnLeft = QPushButton(self.tab)
        self.btnLeft.setObjectName(u"btnLeft")
        self.btnLeft.setEnabled(True)
        self.btnLeft.setGeometry(QRect(10, 200, 30, 30))
        self.btnForward = QPushButton(self.tab)
        self.btnForward.setObjectName(u"btnForward")
        self.btnForward.setEnabled(True)
        self.btnForward.setGeometry(QRect(60, 160, 30, 30))
        self.btnRight = QPushButton(self.tab)
        self.btnRight.setObjectName(u"btnRight")
        self.btnRight.setEnabled(True)
        self.btnRight.setGeometry(QRect(110, 200, 30, 30))
        self.btnBackward = QPushButton(self.tab)
        self.btnBackward.setObjectName(u"btnBackward")
        self.btnBackward.setEnabled(True)
        self.btnBackward.setGeometry(QRect(60, 200, 30, 30))
        self.sldHeightAngle = QSlider(self.tab)
        self.sldHeightAngle.setObjectName(u"sldHeightAngle")
        self.sldHeightAngle.setGeometry(QRect(10, 90, 180, 40))
        self.sldHeightAngle.setMinimum(5)
        self.sldHeightAngle.setMaximum(170)
        self.sldHeightAngle.setPageStep(1)
        self.sldHeightAngle.setSliderPosition(45)
        self.sldHeightAngle.setOrientation(Qt.Orientation.Horizontal)
        self.lblHeightAngle = QLabel(self.tab)
        self.lblHeightAngle.setObjectName(u"lblHeightAngle")
        self.lblHeightAngle.setGeometry(QRect(10, 70, 140, 20))
        self.lblInfo = QLabel(self.tab)
        self.lblInfo.setObjectName(u"lblInfo")
        self.lblInfo.setGeometry(QRect(10, 420, 140, 81))
        self.lblInfo.setAlignment(Qt.AlignmentFlag.AlignLeading |
                                  Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.chkXYRestricted = QCheckBox(self.tab)
        self.chkXYRestricted.setObjectName(u"chkXYRestricted")
        self.chkXYRestricted.setGeometry(QRect(10, 380, 191, 24))
        self.btnRotLeft = QPushButton(self.tab)
        self.btnRotLeft.setObjectName(u"btnRotLeft")
        self.btnRotLeft.setEnabled(True)
        self.btnRotLeft.setGeometry(QRect(10, 290, 30, 30))
        self.btnRotUp = QPushButton(self.tab)
        self.btnRotUp.setObjectName(u"btnRotUp")
        self.btnRotUp.setEnabled(True)
        self.btnRotUp.setGeometry(QRect(60, 290, 30, 30))
        self.btnRotRight = QPushButton(self.tab)
        self.btnRotRight.setObjectName(u"btnRotRight")
        self.btnRotRight.setEnabled(True)
        self.btnRotRight.setGeometry(QRect(110, 290, 30, 30))
        self.btnRotDown = QPushButton(self.tab)
        self.btnRotDown.setObjectName(u"btnRotDown")
        self.btnRotDown.setEnabled(True)
        self.btnRotDown.setGeometry(QRect(60, 330, 30, 30))
        self.lbl2 = QLabel(self.tab)
        self.lbl2.setObjectName(u"lbl2")
        self.lbl2.setGeometry(QRect(10, 260, 140, 20))
        self.lbl1 = QLabel(self.tab)
        self.lbl1.setObjectName(u"lbl1")
        self.lbl1.setGeometry(QRect(10, 130, 140, 20))
        self.tabMain.addTab(self.tab, "")
        self.tabHelp = QWidget()
        self.tabHelp.setObjectName(u"tabHelp")
        self.lbl3 = QLabel(self.tabHelp)
        self.lbl3.setObjectName(u"lbl3")
        self.lbl3.setGeometry(QRect(10, 10, 181, 391))
        self.lbl3.setAlignment(Qt.AlignmentFlag.AlignLeading |
                               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.tabMain.addTab(self.tabHelp, "")
        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.sldTranslateDelta, self.btnUp)
        QWidget.setTabOrder(self.btnUp, self.btnForward)
        QWidget.setTabOrder(self.btnForward, self.btnDown)
        QWidget.setTabOrder(self.btnDown, self.btnLeft)
        QWidget.setTabOrder(self.btnLeft, self.tabMain)

        self.retranslateUi(MainWindow)

        self.tabMain.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.btnUp.setText(QCoreApplication.translate("MainWindow", u"UP", None))
        self.lblTranslateDelta.setText(QCoreApplication.translate("MainWindow", u"Step:", None))
        self.btnDown.setText(QCoreApplication.translate("MainWindow", u"DN", None))
        self.btnLeft.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.btnForward.setText(QCoreApplication.translate("MainWindow", u"^", None))
        self.btnRight.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.btnBackward.setText(QCoreApplication.translate("MainWindow", u"v", None))
        self.lblHeightAngle.setText(QCoreApplication.translate("MainWindow", u"Angle:", None))
        self.lblInfo.setText(QCoreApplication.translate("MainWindow", u"Info", None))
        self.chkXYRestricted.setText(QCoreApplication.translate(
            "MainWindow", u"XY restricted", None))
        self.btnRotLeft.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.btnRotUp.setText(QCoreApplication.translate("MainWindow", u"^", None))
        self.btnRotRight.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.btnRotDown.setText(QCoreApplication.translate("MainWindow", u"v", None))
        self.lbl2.setText(QCoreApplication.translate("MainWindow", u"Rotation:", None))
        self.lbl1.setText(QCoreApplication.translate("MainWindow", u"Movement:", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab),
                                QCoreApplication.translate("MainWindow", u"Camera", None))
        self.lbl3.setText(QCoreApplication.translate("MainWindow", u"Keyboard keys:\n"
                                                     "\n"
                                                     "W: Move forward\n"
                                                     "S: Move backward\n"
                                                     "A: Move left\n"
                                                     "D: Move right\n"
                                                     "E: Move up\n"
                                                     "Q: Move down\n"
                                                     "\n"
                                                     "Arrow-L: Rot left\n"
                                                     "Arrow-R: Rot right\n"
                                                     "Arrow-U: Rot up\n"
                                                     "Arrow-D: Rot down", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tabHelp),
                                QCoreApplication.translate("MainWindow", u"Help", None))
# ===========================================================================
macroWindow = MacroWindow()
# ===========================================================================
