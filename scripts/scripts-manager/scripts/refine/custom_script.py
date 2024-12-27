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

        self.parent.statusMessage(f"Running \"{self.modulePath}\".")

        selObjs = self.common.getSelection(extended=False)

        if len(selObjs) > 0:
            for selObj in selObjs:
                self.refine(selObj)
        else:
            self.parent.statusMessage("Nothing selected.")
# ==============================================================================
    def refine(self, selObj) -> None:

        self.parent.statusMessage(f"Refining \"{selObj.Label}\".")

        shape = Part.getShape(selObj, "", needSubElement=False, refine=True)

        FreeCAD.ActiveDocument.addObject("Part::Feature", selObj.Name + "_refined").Shape = shape
        activeObj = FreeCAD.ActiveDocument.ActiveObject

        activeObj.Label = selObj.Label + "_refined"
        activeObj.ViewObject.LineColor = selObj.ViewObject.LineColor
        activeObj.ViewObject.ShapeColor = selObj.ViewObject.ShapeColor

        FreeCAD.ActiveDocument.recompute()
# ==============================================================================
    def about(self) -> str:

        aboutStr = ("Refine a shape by merging sub object and cleaning up extra edges.\n"
                    "For example, an imported OpenSCAD model.")

        return aboutStr
# ==============================================================================
