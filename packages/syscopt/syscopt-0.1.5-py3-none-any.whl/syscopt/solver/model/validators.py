from abc import ABC, abstractmethod

from numpy.linalg import eig

from solver.model.domain import (
    CardQP,
    ICard,
    CardLogReg, DISCARTSettings
)
from solver.exeptions import ModelingError, SettingsError


class MessageMixin:
    @staticmethod
    def show_valid_msg():
        print("model validated successfully")


class IValidator(ABC, MessageMixin):
    @abstractmethod
    def __init__(self, problem: ICard):
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass


class CardQPValidator(IValidator):

    def __init__(self, qp: CardQP):
        self.qp = qp

    def is_valid(self) -> bool:

        self._check_size()
        self._is_convex()
        return True

    def _check_size(self):

        if self.qp.nvars < 1:
            raise ModelingError("number of variables must be positive")
        if self.qp.nzeros < 1:
            raise ModelingError("number of non-zeros must be positive")
        if self.qp.nzeros > self.qp.nvars:
            raise ModelingError("number of non-zeros cannot be greater that number of variables")
        if self.qp.Q.shape != (self.qp.nvars, self.qp.nvars):
            raise ModelingError("matrix Q is not square")
        if self.qp.c.shape != (self.qp.nvars, 1):
            raise ModelingError("vector c is not a column vector")
        if type(self.qp.d) != float:
            raise ModelingError("d is not a floating point number")

    def _is_convex(self):
        eigs = eig(self.qp.Q)[0]
        for eig_val in eigs:
            if float(eig_val) < 0:
                raise ModelingError("The model is not convex")
        return True


class CardLogRegValidator(IValidator):
    def __init__(self, logreg: CardLogReg):
        self.logreg = logreg

    def is_valid(self) -> bool:
        try:
            self._check_size()
            return True
        except ModelingError as error:
            print(error)
        return False

    def _check_size(self):
        if self.logreg.nvars < 0:
            raise ModelingError("number of variables must be positive")
        if self.logreg.nzeros < 0:
            raise ModelingError("number of non-zeros must be positive")
        if self.logreg.nzeros > self.logreg.nvars:
            raise ModelingError("number of non-zeros cannot be greater that number of variables")
        if self.logreg.nsamples < self.logreg.nvars:
            raise ModelingError("SysCopt does not support nsamples < _nvars")


class SettingsValidator(IValidator):
    def __init__(self, settings: DISCARTSettings):
        self.settings = settings

    def is_valid(self) -> bool:
        try:
            self._validate()
            return True
        except SettingsError as error:
            raise ModelingError(error)

    def _validate(self):
        if self.settings.algorithm < 0:
            raise SettingsError("algorithm setting cannot be negative")
        if self.settings.algorithm > 2:
            raise SettingsError("algorithm setting cannot be greater than 2")

    def show_valid_msg(self):
        print("settings validated successfully")
