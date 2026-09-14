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
*   This macro allows for precise positioning of the camera.              *
*                                                                         *
*   It supports:                                                          *
*   - Camera's translation.                                               *
*   - Camera's field (angle) of view (FOV).                               *
*                                                                         *
*   Doesn't support yet:                                                  *
*   - Camera's rotation.                                                  *
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
import math

from PySide.QtGui import *
from PySide.QtCore import *

import FreeCAD
import FreeCADGui
from pivy.coin import SbVec3f
# ==================================================================================================
__title__ = "CameraControl"
__version__ = "1.0"
__date__ = "14/09/2026"
__author__ = "Naveed Alam"
__Requires__ = "Freecad 1.0.0"
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
            Qt.Key.Key_Q
        )

        self.keysMap = {
            Qt.Key.Key_W: "forward",
            Qt.Key.Key_S: "backward",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_D: "right",
            Qt.Key.Key_E: "up",
            Qt.Key.Key_Q: "down"
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

        # styleSheet = "QPushButton {font-size: 12px; min-width: 30px; max-width: 30px;}"
        styleSheet = "QPushButton {min-width: 30px; max-width: 30px;}"
        self.setStyleSheet(styleSheet)

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
    def translateCamera(self, direction: str) -> None:

        camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

        cameraPosition = camera.position.getValue()
        cameraOrientation = camera.orientation.getValue()

        # Local forward in camera space is (0, 0, –1).
        localForward = SbVec3f(0, 0, -1)

        localLeft = SbVec3f(-1, 0, 0)
        localDown = SbVec3f(0, -1, 0)

        # Rotate by the camera's orientation to get world-space directions.
        worldForward = cameraOrientation.multVec(localForward)
        worldLeft = cameraOrientation.multVec(localLeft)
        worldDown = cameraOrientation.multVec(localDown)

        step = self.deltaTranslation

        if direction in ["forward", "backward"]:
            x = worldForward.getValue()[0]
            y = worldForward.getValue()[1]
            z = worldForward.getValue()[2]
        elif direction in ["left", "right"]:
            x = worldLeft.getValue()[0]
            y = worldLeft.getValue()[1]
            z = worldLeft.getValue()[2]
        elif direction in ["up", "down"]:
            x = worldDown.getValue()[0]
            y = worldDown.getValue()[1]
            z = worldDown.getValue()[2]
        else:
            return

        cameraDirection = FreeCAD.Vector(x, y, z).normalize()

        if direction in ["forward", "left", "down"]:
            dx = cameraDirection.x
            dy = cameraDirection.y
            dz = cameraDirection.z
        elif direction in ["backward", "right", "up"]:
            dx = -cameraDirection.x
            dy = -cameraDirection.y
            dz = -cameraDirection.z
        else:
            return

        translation = FreeCAD.Vector(dx * step, dy * step, dz * step)
        newCameraPosition = FreeCAD.Vector(cameraPosition.getValue()) + translation

        camera.position.setValue(newCameraPosition)

        if hasattr(camera, "heightAngle"):
            camera.heightAngle.setValue(math.radians(self.heightAngle))

        cameraPosition = FreeCAD.Vector(camera.position.getValue().getValue())

        # print(camera.orientation.getValue().getValue())

        cameraOrientationTuple = camera.orientation.getValue().getValue()

        cameraOrientation = FreeCAD.Rotation(
            cameraOrientationTuple[0],
            cameraOrientationTuple[1],
            cameraOrientationTuple[2],
            cameraOrientationTuple[3]
        )

        cameraOrientationAngle = round(math.degrees(cameraOrientation.Angle), 2)

        cameraPositionX = int(newCameraPosition.x / step) * step
        cameraPositionY = int(newCameraPosition.y / step) * step
        cameraPositionZ = int(newCameraPosition.z / step) * step

        self.ui.lblInfo.setText(
            f"X: {cameraPositionX}\n"
            f"Y: {cameraPositionY}\n"
            f"Z: {cameraPositionZ}\n"
            f"OAngle: {cameraOrientationAngle}\n"
            f"OAxis: {round(cameraOrientation.Axis.x, 2)}, "
            f"{round(cameraOrientation.Axis.y, 2)}, "
            f"{round(cameraOrientation.Axis.z, 2)}"
        )

        FreeCADGui.updateGui()
# ==================================================================================================
    def sldTranslateDeltaChanged(self) -> None:

        self.deltaTranslation = float(2 ** self.ui.sldTranslateDelta.value())
        self.ui.lblTranslateDelta.setText(f"Step size: {self.deltaTranslation:g}")
# ==================================================================================================
    def sldHeightAngleChanged(self) -> None:

        self.heightAngle = self.ui.sldHeightAngle.value()
        self.ui.lblHeightAngle.setText(f"FOV: {self.heightAngle:g}")

        camera = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

        if hasattr(camera, "heightAngle"):
            camera.heightAngle.setValue(math.radians(self.heightAngle))
# ==================================================================================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(160, 360)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(160, 360))
        MainWindow.setMaximumSize(QSize(160, 360))
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
        self.tabMain.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabMain.setDocumentMode(True)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.btnUp = QPushButton(self.tab)
        self.btnUp.setObjectName(u"btnUp")
        self.btnUp.setEnabled(True)
        self.btnUp.setGeometry(QRect(110, 140, 40, 40))
        self.sldTranslateDelta = QSlider(self.tab)
        self.sldTranslateDelta.setObjectName(u"sldTranslateDelta")
        self.sldTranslateDelta.setGeometry(QRect(10, 30, 140, 40))
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
        self.btnDown.setGeometry(QRect(10, 140, 40, 40))
        self.btnLeft = QPushButton(self.tab)
        self.btnLeft.setObjectName(u"btnLeft")
        self.btnLeft.setEnabled(True)
        self.btnLeft.setGeometry(QRect(10, 190, 40, 40))
        self.btnForward = QPushButton(self.tab)
        self.btnForward.setObjectName(u"btnForward")
        self.btnForward.setEnabled(True)
        self.btnForward.setGeometry(QRect(60, 140, 40, 40))
        self.btnRight = QPushButton(self.tab)
        self.btnRight.setObjectName(u"btnRight")
        self.btnRight.setEnabled(True)
        self.btnRight.setGeometry(QRect(110, 190, 40, 40))
        self.btnBackward = QPushButton(self.tab)
        self.btnBackward.setObjectName(u"btnBackward")
        self.btnBackward.setEnabled(True)
        self.btnBackward.setGeometry(QRect(60, 190, 40, 40))
        self.sldHeightAngle = QSlider(self.tab)
        self.sldHeightAngle.setObjectName(u"sldHeightAngle")
        self.sldHeightAngle.setGeometry(QRect(10, 90, 140, 40))
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
        self.lblInfo.setGeometry(QRect(10, 240, 140, 80))
        self.tabMain.addTab(self.tab, "")
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
        self.lblTranslateDelta.setText(QCoreApplication.translate(
            "MainWindow", u"Step: 1234567890", None))
        self.btnDown.setText(QCoreApplication.translate("MainWindow", u"DN", None))
        self.btnLeft.setText(QCoreApplication.translate("MainWindow", u"LT", None))
        self.btnForward.setText(QCoreApplication.translate("MainWindow", u"FD", None))
        self.btnRight.setText(QCoreApplication.translate("MainWindow", u"RT", None))
        self.btnBackward.setText(QCoreApplication.translate("MainWindow", u"BD", None))
        self.lblHeightAngle.setText(QCoreApplication.translate(
            "MainWindow", u"Angle: 360 degrees", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tab),
                                QCoreApplication.translate("MainWindow", u"Camera", None))
# ===========================================================================
macroWindow = MacroWindow()
# ===========================================================================
