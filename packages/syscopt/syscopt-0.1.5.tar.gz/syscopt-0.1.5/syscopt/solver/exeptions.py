class ModelingError(Exception):
    pass


class SettingsError(Exception):
    pass


class NLPSubSolverError(Exception):
    pass


class NotRecognizedModel(ModelingError):
    pass


class DIPOAError(Exception):
    pass
