from abc import ABC, abstractmethod
from dataclasses import dataclass

from numpy import (
    ndarray,
    exp,
    log,
    diagflat,
    zeros
)

RHADMM_MAXITER = 1000
RHADMM_PRES = 1e-8
RHADMM_DRES = 1e-8
RHADMM_RHO = 0.01
DIPOA_MAXITER = 500
DIPOA_GAP = 1e-3
DIPOA_RELGAP = DIPOA_GAP
BIG_M = 0.6
ZERO = zeros((1, 1))
ON = True
OFF = False
INF = 1e9


class ICard(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def obj_at(self, x: ndarray) -> float:
        pass

    @abstractmethod
    def grad_at(self, x: ndarray) -> ndarray:
        pass

    @abstractmethod
    def hess_at(self, x: ndarray = None) -> ndarray:
        pass

    @property
    @abstractmethod
    def nvars(self):
        pass

    @nvars.setter
    @abstractmethod
    def nvars(self, value):
        pass

    @property
    @abstractmethod
    def nzeros(self):
        pass

    @nzeros.setter
    @abstractmethod
    def nzeros(self, value):
        pass


class CardQP(ICard):
    def __init__(self, Q: ndarray, c: ndarray, d: float, nzeros: int = 0):
        self.Q, self.c, self.d = Q, c, d
        self._nvars = self.Q.shape[0]
        self._nzeros = nzeros

    @property
    def nzeros(self):
        return self._nzeros

    @nzeros.setter
    def nzeros(self, value: int):
        self._nzeros = value

    @property
    def nvars(self):
        return self._nvars

    @nvars.setter
    def nvars(self, value: int):
        self._nvars = value

    def obj_at(self, x: ndarray) -> float:
        return float(0.5 * x.T @ self.Q @ x + self.c.T @ x + self.d)

    def grad_at(self, x: ndarray) -> ndarray:
        return self.Q @ x + self.c

    def hess_at(self, x: ndarray = None) -> ndarray:
        return self.Q


class CardLogReg(ICard):

    def __init__(self, X: ndarray, y: ndarray, nzeros: int = 0):
        self.X, self.y = X, y
        self.nsamples, self._nvars = self.X.shape
        self._nzeros = nzeros

    def obj_at(self, x: ndarray) -> float:
        h = self._h(x)
        f = -self.y.T @ log(h) - (1 - self.y).T @ log(1 - h)
        return (1 / self.nsamples) * float(f)

    def _h(self, x: ndarray) -> ndarray:
        z: ndarray = self.X @ x
        h: ndarray = 1 / (1 + exp(-z))
        h[h == 1] = 1 - 1e-8
        h[h == 0] = 1e-8
        return h

    def grad_at(self, x: ndarray):
        h = self._h(x)

        return (1 / self.nsamples) * self.X.T @ (h - self.y)

    def hess_at(self, x: ndarray = None) -> ndarray:
        assert x is not None, "x cannot be None"
        h = self._h(x)
        return (1 / self.nsamples) * self.X.T @ diagflat(h * (1 - h)) @ self.X

    @property
    def nzeros(self):
        return self._nzeros

    @nzeros.setter
    def nzeros(self, value: int):
        self._nzeros = value

    @property
    def nvars(self):
        return self._nvars

    @nvars.setter
    def nvars(self, value: int):
        self._nvars = value


@dataclass
class NLPSolution:
    status: int
    sol: ndarray
    objval: float


@dataclass
class RHADMMSettings:
    maxiter: int = RHADMM_MAXITER
    pres: float = RHADMM_PRES
    dres: float = RHADMM_DRES
    rho: float = RHADMM_RHO
    adaptive_rho: bool = ON
    verbose: bool = OFF


@dataclass
class DIPOASettings:
    maxiter: int = DIPOA_MAXITER
    gap: float = DIPOA_GAP
    rgap: float = DIPOA_RELGAP
    sos: bool = ON
    soc: bool = OFF
    verbose: bool = ON
    big_m: float = BIG_M
    hybrid: bool = OFF


@dataclass
class DISOASettings:
    sos: bool = ON
    verbose: bool = ON
    big_m: float = BIG_M


@dataclass
class RHADMMSolution:
    x: ndarray  # solution
    fx: float  # local fx
    tfx: float  # total fx
    gx: ndarray  # gradient at solution
    status: int  # status
    wct: float = INF  # wall clock time


@dataclass
class LinearHyperPlane:
    x: ndarray
    fx: float
    gfx: ndarray


@dataclass
class QuadraticHyperPlane(LinearHyperPlane):
    eig: float


@dataclass
class MIPSolution:
    binvar: ndarray
    x: ndarray
    objval: float
    wct: float
    status: int


@dataclass
class DISCARTSolution:
    x: ndarray = ZERO
    objval: float = 0.0
    wct: float = 0.0
    status: int = -1
    maxiter: int = 0
    num_foc: int = 0
    num_soc: int = 0
    total_nlp_time: int = 0
    total_mip_time: int = 0
    num_lazy_constrs: int = 0
    num_hybrid_soc: int = 0,
    algorithm: str = "",
    model: str = ""

    def __str__(self):

        if self.maxiter == 0:
            termination_msg = f"\ndiscart converged successfully"
        else:
            termination_msg = f"\ndiscart converged successfully in {self.maxiter} iterations"

        if self.status == 0:
            status = "optimal"
        else:
            status = "maximum number of iteration reached"

        res_text = f"solver information:\n" \
                   f"\talgorithm: {self.algorithm}\n" \
                   f"\tmodel: {self.model}\n" \
                   f"\tstatus: {status}\n" \
                   f"\ttotal NLP time: {self.total_nlp_time:5.4f} seconds\n" \
                   f"\ttotal MIP time: {self.total_mip_time:5.4f} seconds\n" \
                   f"\tsyscopt time: {self.wct:5.4f} seconds\n" \
                   f"\ttotal NLP per total time: {self.total_nlp_time / self.wct * 100:3.3f}%\n" \
                   f"\ttotal MIP per total time: {self.total_mip_time / self.wct * 100:3.3f}%\n" \
                   f"solution information:\n" \
                   f"\tobjective value: {self.objval:5.6f}\n" \
                   f"\tnumber of linear cuts: {self.num_foc}\n" \
                   f"\tnumber of quadratic cuts: {self.num_soc}\n" \
                   f"\tnumber of lazy constraints: {self.num_lazy_constrs}\n" \
                   f"\tnumber of hybrid constraints: {self.num_hybrid_soc}\n" \
                   f"see log.txt file for more detailed information"

        return termination_msg + "\n" + res_text


@dataclass
class DISCARTSettings:
    algorithm: int = 0
    dipoa_opts: DIPOASettings = DIPOASettings()
    disoa_opts: DISOASettings = DISOASettings()
    verbose: bool = ON
    big_m: float = BIG_M
    sos: bool = OFF


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
