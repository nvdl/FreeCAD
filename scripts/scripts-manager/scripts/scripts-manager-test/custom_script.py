from time import sleep
# ==============================================================================
class CustomScript():

    def __init__(self, parent, modulePath) -> None:

        self.parent = parent
        self.modulePath = modulePath
# ==============================================================================
    def run(self) -> None:

        sub1 = self.parent.getModule(modulePath=self.modulePath, name="sub_module_one", relative=True)
        sub1.hello()

        sub2 = self.parent.getModule(modulePath=self.modulePath, name="sub_module_two", relative=True)
        sub2.test()

        sleep(0.25)

        # modulePath="common": "common" is the name of the directory.
        # name="common": "common" is the name of the sub-module/script i.e. "common.py".
        common = self.parent.getModule(modulePath="common", name="common", relative=False)

        selection = common.getSelection(extended=False)

        self.parent.messageBoxInformation(title="Information", message="Information")
        self.parent.messageBoxWarning(title="Warning", message="Warning")
        self.parent.messageBoxCritical(title="Critical", message="Critical")
# ==============================================================================
    def about(self) -> str:

        aboutStr = "This is a test script using the common module and two extra modules."

        return aboutStr
# ==============================================================================
