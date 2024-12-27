import FreeCADGui
# ==============================================================================
def getSelection(extended):

    if extended:
        selObjs = FreeCADGui.Selection.getSelectionEx()
    else:
        selObjs = FreeCADGui.Selection.getSelection()

    return selObjs
# ==============================================================================
