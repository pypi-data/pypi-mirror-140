from testwizard.commands_core.ResultBase import ResultBase

class GetElementResult(ResultBase):
    def __init__(self, result, successMessage, failMessage):
        ResultBase.__init__(self, result["ok"] is True, successMessage, failMessage + ": " + result["errorMessage"])

        self.element = result["element"]