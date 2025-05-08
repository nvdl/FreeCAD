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
*   This macro acts as a scripts' manager.                                *
*   Scripts should be placed in a directory named "scripts".              *
*   This script and the "scripts" directory should be in the same parent  *
*   directory.                                                            *
*   Each custom script needs its own directory containing the main        *
*   script named "custom_script.py".                                      *
*                                                                         *
*   The main script, "custom_script.py", should contain a class as        *
*   below:                                                                *
*                                                                         *
*   class CustomScript():                                                 *
*       def __init__(self, parent, modulePath) -> None:                   *
*           self.parent = parent                                          *
*           self.modulePath = modulePath                                  *
*       def run(self) -> None:                                            *
*           // Code to run.                                               *
*       def about(self) -> str:                                           *
*           // Helpful information about the script.                      *
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
# ==============================================================================
import os
import sys
import pathlib
import importlib

from PySide.QtGui import *
from PySide.QtCore import *

import FreeCAD
import FreeCADGui
# ==============================================================================
__title__ = "Scripts Manager"
__version__ = "1.3"
__date__ = "08/05/2025"
__author__ = "Naveed Alam"
__Requires__ = "Freecad 1.0.0"
__Status__ = "stable"
__Comment__ = "This macro manages other scripts."
__url__ = "http://www.freecadweb.org/"
__Web__ = "http://www.freecadweb.org/"
__Wiki__ = "http://www.freecadweb.org/wiki/"
__License__ = "LGPL-2.0-or-later"
__Icon__ = ""
__IconW__ = ""
__Help__ = ""
# ==============================================================================
class MacroWindow(QMainWindow):

    def __init__(self, parent) -> None:

        super(MacroWindow, self).__init__(parent)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        # self.consoleMessage(f"{scriptDir=}\n")

        scriptsDir = pathlib.Path(scriptDir).joinpath("scripts")
        # self.consoleMessage(f"{scriptsDir=}\n")

        if scriptsDir not in sys.path:
            sys.path.append(str(scriptsDir))

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{__title__} v{__version__}")

        self.importedScripts = {}

        self.scriptsData: dict[str, str] = {}

        for path in pathlib.Path(scriptsDir).iterdir():
            if path.is_dir():
                pathName = path.name

                # Skip directories starting with special characters.
                if pathName[0] in [".", "_"]:
                    continue

                # self.consoleMessage(f"{path=}\n")

                # Load/reload all ".py" files.
                for child in path.iterdir():
                    if child.suffix == ".py":
                        modulePath = pathName + "." + child.stem
                        # self.consoleMessage(f"{modulePath=}\n")

                        if modulePath in sys.modules:
                            # self.consoleMessage(f"Reloading {modulePath=}.\n")
                            del sys.modules[modulePath]
                            importlib.import_module(modulePath)
                            # importlib.reload(sys.modules[modulePath])
                        else:
                            # self.consoleMessage(f"Loading {modulePath=}.\n")
                            try:
                                importlib.import_module(modulePath)
                            except:
                                self.consoleError(f"Failed to load \"{modulePath}\".\n")
                                continue

                modulePath = pathName + ".custom_script"
                # self.consoleMessage(f"{modulePath=}\n")

                if modulePath in sys.modules:
                    importedModule = sys.modules[modulePath]
                    # self.consoleMessage(f"{importedModule=}\n")

                    if hasattr(importedModule, "CustomScript"):
                        self.importedScripts[pathName] = (importedModule, modulePath)
                    else:
                        self.consoleError(f"{importedModule} has no \"CustomScript\" class.\n")
                else:
                    # self.consoleMessage(f"\"{modulePath}\" not found.\n")
                    pass

        self.importedScripts = dict(sorted(self.importedScripts.items()))

        for pathName in self.importedScripts:
            self.ui.lstScripts.addItem(pathName)

        self.ui.chkAlwaysOnTop.clicked.connect(self.chkAlwaysOnTopClicked)

        self.ui.btnRunScript.clicked.connect(self.btnRunScriptClicked)
        self.ui.btnAboutScript.clicked.connect(self.btnAboutScriptClicked)
        self.ui.btnClearFilter.clicked.connect(self.btnClearFilterClicked)

        self.ui.lstScripts.itemDoubleClicked.connect(self.lstScriptsItemDoubleClicked)
        self.ui.lneFilter.textChanged.connect(self.lneFilterTextChanged)

        self.ui.txtAbout.setText("Right click, copy the URL and paste it into your browser "
                                 "to access the Git repository.<br><br>"
                                 "<a href=\"https://github.com/nvdl/FreeCAD\">https://github.com/nvdl/FreeCAD</a>")

        self.ui.txtAbout.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)

        self.ui.btnClearFilter.setStyleSheet("text-align: left")

        self.chkAlwaysOnTopClicked()
# ==============================================================================
    def chkAlwaysOnTopClicked(self) -> None:

        flags = self.windowFlags()

        if self.ui.chkAlwaysOnTop.isChecked():
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & (~Qt.WindowStaysOnTopHint))

        self.show()
# ==============================================================================
    def btnRunScriptClicked(self):

        currentItem = self.ui.lstScripts.currentItem()

        if currentItem is not None:
            self.runScript(currentItem.text())
# ==============================================================================
    def btnAboutScriptClicked(self):

        currentItem = self.ui.lstScripts.currentItem()

        if currentItem is not None:
            name = currentItem.text()
            importedScript = self.getScript(name)
            if hasattr(importedScript, "about"):
                aboutStr = importedScript.about()
            else:
                aboutStr = "No information available."

            self.messageBoxInformation(f"Script: {name}", aboutStr)
# ==============================================================================
    def btnClearFilterClicked(self):

        self.ui.lneFilter.clear()
# ==============================================================================
    def lstScriptsItemDoubleClicked(self, item) -> None:

        self.runScript(item.text())
# ==============================================================================
    def lneFilterTextChanged(self):

        filterText = self.ui.lneFilter.text()
        self.ui.lstScripts.clear()

        for pathName in self.importedScripts:
            if filterText in pathName:
                self.ui.lstScripts.addItem(pathName)
# ==============================================================================
    def runScript(self, name):

        importedScript = self.getScript(name)

        if hasattr(importedScript, "run"):
            self.ui.btnRunScript.setStyleSheet("background-color: #600000")
            self.ui.btnRunScript.repaint()

            self.ui.statusBar.showMessage(f"Running: \"{name}\"")
            self.ui.statusBar.repaint()

            importedScript.run()

            self.ui.btnRunScript.setStyleSheet("")
            self.ui.btnRunScript.repaint()
        else:
            self.messageBoxInformation(f"Script: {name}", "\"CustomScript\" class has no \"run\" function.")
# ==============================================================================
    def getScript(self, name):

        importedModule, modulePath = self.importedScripts[name]
        importedScript = importedModule.CustomScript(self, modulePath)

        return importedScript
# ==============================================================================
    def getModule(self, modulePath, name, relative):

        if relative:
            moduleToLoad = ".".join(modulePath.split(".")[:-1]) + "." + name
        else:
            moduleToLoad = modulePath + "." + name

        importedModule = sys.modules[moduleToLoad]

        return importedModule
# ==============================================================================
    def setScriptData(self, key: str, data: str) -> None:
        """
        Used by scripts to share data with each other.
        A script can save data as a string using a key which
        can be retrieved by the another script using the same key.
        """

        self.scriptsData[key] = data
# ==============================================================================
    def getScriptData(self, key: str) -> str | None:
        """
        Used by scripts to share data with each other.
        A script can save data as a string using a key which
        can be retrieved by the another script using the same key.
        """

        ret = None

        if key in self.scriptsData:
            ret = self.scriptsData[key]

        return ret
# ==============================================================================
    def messageBoxInformation(self, title: str, message: str) -> None:

        QMessageBox.information(self, title, message, QMessageBox.Ok)
# ==============================================================================
    def messageBoxWarning(self, title: str, message: str) -> None:

        QMessageBox.warning(self, title, message, QMessageBox.Ok)
# ==============================================================================
    def messageBoxCritical(self, title: str, message: str) -> None:

        QMessageBox.critical(self, title, message, QMessageBox.Ok)
# ==============================================================================
    def messageBoxYesNo(self, title: str, message: str) -> bool:

        ret = (QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes)

        return ret
# ==============================================================================
    def inputDialog(self, title: str, message: str):

        text, status = QInputDialog.getText(self, title, message)

        return (text, status)
# ==============================================================================
    def fileSaveDialog(self, title: str, filters: str):

        fName, selectedFilter = QFileDialog.getSaveFileName(self, title, "", filters)

        return (fName, selectedFilter)
# ==============================================================================
    def colorDialog(self, initialColor: tuple[float, float, float]) -> tuple[float, float, float, bool]:

        status = False

        r = int(initialColor[0] * 255)
        g = int(initialColor[1] * 255)
        b = int(initialColor[2] * 255)

        color = QColorDialog.getColor(QColor(r, g, b), None)

        if color.isValid():
            r = color.red()
            g = color.green()
            b = color.blue()
            status = True

        return (r, g, b, status)
# ==============================================================================
    def optionsDialog(self, mode, prompt, options) -> tuple[list[str], bool]:

        winOptions = WindowOptions(self, mode, prompt, options)

        while winOptions.isVisible():
            QApplication.instance().processEvents()
            QThread.msleep(50)

        return winOptions.options()
# ==============================================================================
    def statusMessage(self, message) -> None:

        if message != "":
            self.ui.statusBar.showMessage(message)
        else:
            self.ui.statusBar.clearMessage()

        self.ui.statusBar.repaint()
# ==============================================================================
    @staticmethod
    def consoleMessage(message) -> None:

        FreeCAD.Console.PrintMessage(f"ScriptsManager: {message}\n")
# ==============================================================================
    @staticmethod
    def consoleError(message) -> None:

        FreeCAD.Console.PrintError(f"ScriptsManager: {message}\n")
# ==============================================================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(300, 480)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(300, 480))
        MainWindow.setMaximumSize(QSize(300, 480))
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
        self.tabMain.setGeometry(QRect(0, 0, 300, 461))
        self.tabMain.setIconSize(QSize(16, 16))
        self.tabMain.setElideMode(Qt.ElideNone)
        self.tabMain.setDocumentMode(True)
        self.tabScripts = QWidget()
        self.tabScripts.setObjectName(u"tabScripts")
        self.lstScripts = QListWidget(self.tabScripts)
        self.lstScripts.setObjectName(u"lstScripts")
        self.lstScripts.setGeometry(QRect(10, 50, 280, 320))
        self.btnRunScript = QPushButton(self.tabScripts)
        self.btnRunScript.setObjectName(u"btnRunScript")
        self.btnRunScript.setEnabled(True)
        self.btnRunScript.setGeometry(QRect(155, 380, 135, 40))
        self.lneFilter = QLineEdit(self.tabScripts)
        self.lneFilter.setObjectName(u"lneFilter")
        self.lneFilter.setGeometry(QRect(50, 10, 200, 30))
        self.lblFilter = QLabel(self.tabScripts)
        self.lblFilter.setObjectName(u"lblFilter")
        self.lblFilter.setGeometry(QRect(10, 15, 50, 20))
        self.btnAboutScript = QPushButton(self.tabScripts)
        self.btnAboutScript.setObjectName(u"btnAboutScript")
        self.btnAboutScript.setEnabled(True)
        self.btnAboutScript.setGeometry(QRect(10, 380, 135, 40))
        self.btnClearFilter = QPushButton(self.tabScripts)
        self.btnClearFilter.setObjectName(u"btnClearFilter")
        self.btnClearFilter.setEnabled(True)
        self.btnClearFilter.setGeometry(QRect(260, 10, 30, 30))
        self.tabMain.addTab(self.tabScripts, "")
        self.tabView = QWidget()
        self.tabView.setObjectName(u"tabView")
        self.chkAlwaysOnTop = QCheckBox(self.tabView)
        self.chkAlwaysOnTop.setObjectName(u"chkAlwaysOnTop")
        self.chkAlwaysOnTop.setGeometry(QRect(10, 10, 180, 30))
        self.tabMain.addTab(self.tabView, "")
        self.tabAbout = QWidget()
        self.tabAbout.setObjectName(u"tabAbout")
        self.txtAbout = QTextEdit(self.tabAbout)
        self.txtAbout.setObjectName(u"txtAbout")
        self.txtAbout.setGeometry(QRect(10, 10, 280, 400))
        self.tabMain.addTab(self.tabAbout, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        self.tabMain.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.btnRunScript.setText(QCoreApplication.translate("MainWindow", u"Run Script", None))
        self.lblFilter.setText(QCoreApplication.translate("MainWindow", u"Filter", None))
        self.btnAboutScript.setText(QCoreApplication.translate("MainWindow", u"About Script", None))
        self.btnClearFilter.setText(QCoreApplication.translate("MainWindow", u"<<<", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tabScripts),
                                QCoreApplication.translate("MainWindow", u"Scripts", None))
        self.chkAlwaysOnTop.setText(QCoreApplication.translate("MainWindow", u"Always on top", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tabView),
                                QCoreApplication.translate("MainWindow", u"View", None))
        self.tabMain.setTabText(self.tabMain.indexOf(self.tabAbout),
                                QCoreApplication.translate("MainWindow", u"About", None))
# ==============================================================================
class WindowOptions(QMainWindow):

    def __init__(self, parent: QMainWindow, mode, prompt, options) -> None:

        super(WindowOptions, self).__init__(parent)

        winWidth = parent.width()
        winHeight = parent.height()

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(winWidth, winHeight))
        self.setMaximumSize(QSize(winWidth, winHeight))
        # self.resize(winWidth, winHeight)

        self.move(parent.pos().x() - (winWidth + 10), parent.pos().y())

        if mode == "single":
            self.setWindowTitle("Single Option Mode")
        elif mode == "multiple":
            self.setWindowTitle("Multiple Options Mode")
        else:
            assert False, "Wrong mode."

        self.lblPrompt = QLabel(self)
        self.lblPrompt.resize(280, 20)
        self.lblPrompt.move(10, 10)
        self.lblPrompt.setText(prompt)

        self.lstOptions = QListWidget(self)
        self.lstOptions.resize(280, 380)
        self.lstOptions.move(10, 40)
        self.lstOptions.itemDoubleClicked.connect(self.listItemDoubleClicked)
        self.lstOptions.setContextMenuPolicy(Qt.CustomContextMenu)

        if mode == "single":
            self.lstOptions.setSelectionMode(QAbstractItemView.SingleSelection)
        elif mode == "multiple":
            self.lstOptions.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            assert False, "Wrong mode."

        self.btnOK = QPushButton("OK", self)
        self.btnOK.resize(135, 40)
        self.btnOK.move(10, 430)
        self.btnOK.clicked.connect(self.btnOKClicked)

        self.btnCancel = QPushButton("Cancel", self)
        self.btnCancel.resize(135, 40)
        self.btnCancel.move(155, 430)
        self.btnCancel.clicked.connect(self.btnCancelClicked)

        for option in options:
            self.lstOptions.addItem(option)

        self.optionsSelected: list[str] = []
        self.statusSelection = False

        self.show()
# ==============================================================================
    def listItemDoubleClicked(self, item) -> None:

        self.optionsSelected = self.selectedItems()
        self.statusSelection = True

        self.hide()
# ==============================================================================
    def btnOKClicked(self):

        self.optionsSelected = self.selectedItems()
        self.statusSelection = True

        self.hide()
# ==============================================================================
    def btnCancelClicked(self):

        self.hide()
# ==============================================================================
    def selectedItems(self):

        return [item.text() for item in self.lstOptions.selectedItems()]
# ==============================================================================
    def options(self) -> tuple[list[str], bool]:

        return self.optionsSelected, self.statusSelection
# ==============================================================================
macroWindow = MacroWindow(FreeCADGui.getMainWindow())
# ==============================================================================
