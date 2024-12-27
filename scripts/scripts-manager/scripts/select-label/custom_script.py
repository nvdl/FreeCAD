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

        if len(selObjs) > 0:
            self.parent.setScriptData(key="selectionLabel", data=selObjs[0].Label)
        else:
            self.parent.statusMessage("Nothing selected.")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Get label of the first item in the selection and save it."

        return aboutStr
# ==============================================================================
