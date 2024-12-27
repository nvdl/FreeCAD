import FreeCAD
import FreeCADGui
import Part
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

        placement = self.parent.getScriptData(key="objectPlacement")

        if placement is None:
            self.parent.statusMessage("No data found.")

            self.parent.messageBoxInformation(self.modulePath,
                                              ("No data found.\n"
                                               "Please use the selection script to choose the placement of the target objects."))

            return

        for selObj in selObjs:
            selObj.Placement = placement
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Set placement (position and rotation) of objects using the saved information."

        return aboutStr
# ==============================================================================
