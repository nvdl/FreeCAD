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

        selObjs = self.common.getSelection(extended=False)

        if len(selObjs) == 0:
            self.parent.statusMessage("Nothing selected.")
            return

        label = self.parent.getScriptData(key="selectionLabel")

        if label is None:
            self.parent.statusMessage("No data found.")

            self.parent.messageBoxInformation(self.modulePath,
                                              ("No data found.\n"
                                               "Please use the selection script to choose the label of the target group."))

            return

        groups = FreeCAD.ActiveDocument.getObjectsByLabel(label)

        if len(groups) > 0:
            group = groups[0]

        if type(group) != FreeCAD.DocumentObjectGroup:
            self.parent.statusMessage("Selection is not a group of objects.")

            self.parent.messageBoxInformation(self.modulePath,
                                              ("Selection is not a group of objects.\n"
                                               "Please use the selection script to choose the label of the target group."))

            return

        for selObj in selObjs:
            group.addObject(selObj)
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Set group label of objects using the saved label of selection.\n"
                    "Use the selection script to choose the label of the target group.")

        return aboutStr
# ==============================================================================
