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

        ret = self.parent.messageBoxYesNo(
            self.modulePath, "This will delete the selected object and all of its sub objects. Continue?")

        if ret:
            FreeCADGui.activateWorkbench("OpenSCADWorkbench")
            FreeCADGui.runCommand("OpenSCAD_RemoveSubtree", 0)

            # TODO: Revert to the correct workbench.
            FreeCADGui.activateWorkbench("PartWorkbench")
        else:
            self.parent.statusMessage("Canceled.")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "Uses \"OpenSCAD_RemoveSubtree\" to delete an object and all of its subobjects."

        return aboutStr
# ==============================================================================
