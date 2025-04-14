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
import os
import re
from pathlib import Path

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

        fNameSettings = Path(FreeCAD.ActiveDocument.FileName).absolute().with_suffix(".FCStdView")

        # self.parent.consoleMessage(f"{fNameSettings=}")

        if not fNameSettings.exists():
            self.parent.statusMessage(f"Settings file \"{fNameSettings.name}\" is missing.")
            return

        # self.parent.consoleMessage("---")
        status, lines = self.importFiles(fNameSettings)
        # self.parent.consoleMessage("---")

        if not status:
            return

        themesVariables: dict[str, dict[str, str]] = {}

        self.getVariables(lines, themesVariables)

        if not self.substituteVariables(themesVariables):
            return

        customThemes = list(filter(lambda theme: theme != "global", themesVariables.keys()))

        if len(customThemes) > 1:
            selection, status = self.parent.optionsDialog("single", customThemes)

            if not status:
                return

            theme = selection[0]

        elif len(customThemes) == 1:
            theme = customThemes[0]

        else:
            theme = None

        if self.updateViewObjects(lines, themesVariables, theme):
            self.parent.statusMessage(f"Done \"{self.modulePath}\"")
        else:
            self.parent.statusMessage(f"Failed \"{self.modulePath}\"")
# ==============================================================================
    @staticmethod
    def readFile(fPath) -> list[str]:

        with open(fPath, "rt", encoding="utf-8") as fData:
            lines = fData.read().splitlines()

        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != "" and not line.startswith("#")]

        lines2 = []

        # Strip away comments at the ends of lines.
        for line in lines:
            pos = line.find("#")

            if pos != -1:
                line = line[:pos].strip()

            lines2.append(line)

        lines = lines2

        return lines
# ==============================================================================
    def importFiles(self, fPath) -> tuple[bool, list[str]]:

        if not fPath.is_file():
            self.parent.messageBoxCritical(self.modulePath, f"\"{fPath}\" not found.")
            return False, []

        # self.parent.consoleMessage(f"Importing \"{fPath}\".")

        lines = self.readFile(fPath)

        status = True
        lines2 = []

        for line in lines:
            match = re.match(r'import\s+"(.+)"', line)

            if match is None:
                lines2.append(line)
                continue

            fPath2 = Path(match.groups()[0])

            if fPath2.is_absolute():
                # self.parent.consoleMessage(f"Already absolute: \"{fPath2}\".")
                pass
            else:
                # self.parent.consoleMessage(f"Converting to absolute: \"{fPath2}\".")
                fPath2 = fPath.parent.joinpath(fPath2)

            # self.parent.consoleMessage(f"{fPath2=}")

            status, linesImported = self.importFiles(fPath2)

            if not status:
                break

            lines2 += linesImported

        return status, lines2
# ==============================================================================
    def getVariables(self, lines, themesVariables) -> None:
        """
        Get values of all variables from all themes.
        """

        for line in lines:
            fields = line.split(",")
            fields = [field.strip() for field in fields]

            # A variable belongs to "global" theme if it does not belong to any other theme.
            if len(fields) == 2:
                theme = "global"
                variableName = fields[0]
                variableValue = fields[1]

            elif len(fields) == 3:
                theme = fields[0]
                variableName = fields[1]
                variableValue = fields[2]

            else:
                continue

            if theme not in themesVariables:
                themesVariables[theme] = {}

            themesVariables[theme][variableName] = variableValue

            # self.parent.consoleMessage(f"{theme=}")
            # self.parent.consoleMessage(f"{variableName=}")
            # self.parent.consoleMessage(f"{variableValue=}")
            # self.parent.consoleMessage("---")
# ==============================================================================
    def substituteVariables(self, themesVariables) -> bool:
        """
        Substitute variables referencing other variables.
        A variable can reference another variable in its own or the "global" theme.
        """

        status = True

        for idx in range(100):
            updated = False

            for theme in themesVariables:
                for variableName in themesVariables[theme]:
                    variableValue = themesVariables[theme][variableName]

                    if "${" not in variableValue:
                        continue

                    variableName2 = variableValue[2:-1]

                    # self.parent.consoleMessage(f"{variableName=}")
                    # self.parent.consoleMessage(f"{variableValue=}")

                    if variableName2 in themesVariables[theme]:
                        themesVariables[theme][variableName] = themesVariables[theme][variableName2]

                    elif "global" in themesVariables and variableName2 in themesVariables["global"]:
                        themesVariables[theme][variableName] = themesVariables["global"][variableName2]

                    else:
                        self.parent.messageBoxCritical(self.modulePath, f"No value found for \"{variableName2}\".")
                        return False

                    # self.parent.consoleMessage(
                    #     f"themesVariables[{theme}][{variableName}]: {themesVariables[theme][variableName]}")

                    # self.parent.consoleMessage("---")

                    updated = True

            if not updated:
                # self.parent.consoleMessage(f"Broke from loop at {idx}.")
                break

        else:
            status = False
            self.parent.messageBoxCritical(self.modulePath, "Too long variable reference chain.")

        return status
# ==============================================================================
    def updateViewObjects(self, lines, themesVariables, theme) -> bool:

        objs = self.common.getAllObjects()
        objs = [obj for obj in objs if hasattr(obj, "ViewObject")]
        objs = [obj for obj in objs if hasattr(obj.ViewObject, "ShapeAppearance")]

        for line in lines:
            fields1 = line.split(",")
            fields1 = [field.strip() for field in fields1]

            if len(fields1) in [2, 3]:
                continue

            if len(fields1) != 11:
                self.parent.messageBoxCritical(self.modulePath, f"Line \"{line}\" has invalid number of fields.")
                return False

            fields = []

            for field in fields1:
                regex = r"\$\{(.*?)\}"
                search = re.findall(regex, field)

                if len(search) > 0:
                    for variableName in search:
                        if theme is not None and variableName in themesVariables[theme]:
                            variableValue = themesVariables[theme][variableName]

                        elif "global" in themesVariables and variableName in themesVariables["global"]:
                            variableValue = themesVariables["global"][variableName]

                        else:
                            self.parent.messageBoxCritical(self.modulePath, f"No value found for \"{variableName}\".")
                            return False

                        # self.parent.consoleMessage(f"{field=}")
                        field = field.replace(f"${{{variableName}}}", variableValue)
                        # self.parent.consoleMessage(f"{field=}")

                    # self.parent.consoleMessage("---")

                fields.append(field)

            regex = fields[0]

            colorDiffuse = self.strToColor(fields[1])
            if colorDiffuse is None:
                return False

            colorAmbient = self.strToColor(fields[2])
            if colorAmbient is None:
                return False

            colorSpecular = self.strToColor(fields[3])
            if colorSpecular is None:
                return False

            colorEmissive = self.strToColor(fields[4])
            if colorEmissive is None:
                return False

            colorLine = self.strToColor(fields[5])
            if colorLine is None:
                return False

            widthLine = self.toFloat(fields[6])
            if widthLine is None:
                return False

            colorPoint = self.strToColor(fields[7])
            if colorPoint is None:
                return False

            sizePoint = self.toFloat(fields[8])
            if sizePoint is None:
                return False

            shininess = self.toFloat(fields[9])
            if shininess is None:
                return False
            shininess /= 100

            transparency = self.toFloat(fields[10])
            if transparency is None:
                return False
            transparency /= 100

            for obj in objs:
                if re.search(regex, obj.Label) is None:
                    continue

                viewObj = obj.ViewObject

                if (transparency < 0) and hasattr(viewObj, "Visibility"):
                    viewObj.Visibility = False
                    continue

                viewObj.ShapeAppearance = FreeCAD.Material(DiffuseColor=colorDiffuse,
                                                           AmbientColor=colorAmbient,
                                                           SpecularColor=colorSpecular,
                                                           EmissiveColor=colorEmissive,
                                                           Shininess=shininess,
                                                           Transparency=transparency)

                if hasattr(viewObj, "LineColor"):
                    viewObj.LineColor = colorLine

                if hasattr(viewObj, "LineWidth"):
                    viewObj.LineWidth = widthLine

                if hasattr(viewObj, "PointColor"):
                    viewObj.PointColor = colorPoint

                if hasattr(viewObj, "PointSize"):
                    viewObj.PointSize = sizePoint

        return True
# ==============================================================================
    def strToColor(self, colorStr) -> tuple[int, int, int] | None:

        if len(colorStr) != 6:
            self.parent.messageBoxCritical(self.modulePath, f"Wrong color value \"{colorStr}\".")
            return None

        r = int(colorStr[0:2], 16)
        g = int(colorStr[2:4], 16)
        b = int(colorStr[4:6], 16)

        return (r, g, b)
# ==============================================================================
    def toFloat(self, strNum) -> float | None:

        try:
            ret = float(strNum)
        except ValueError:
            self.parent.messageBoxCritical(self.modulePath, f"Wrong numerical value \"{strNum}\".")
            ret = None

        return ret
# ==============================================================================
    @staticmethod
    def about() -> str:

        aboutStr = ("Set properties of view objects through regex.\n"
                    "Please refer to the documentation on Github for creating a settings file.")

        return aboutStr
# ==============================================================================
