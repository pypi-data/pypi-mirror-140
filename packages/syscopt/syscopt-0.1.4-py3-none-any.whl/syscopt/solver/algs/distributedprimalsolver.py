from abc import ABC, abstractmethod
from time import time
from typing import Optional

import gurobipy as gp
from gurobipy import GRB
from numpy import (
    zeros,
    ndarray,
    minimum,
    maximum,
    allclose
)
from numpy.linalg import norm
from scipy.optimize import (
    LinearConstraint,
    minimize
)

from solver.DIS import *
from solver.common import MPIManager
from solver.exeptions import NotRecognizedModel, NLPSubSolverError
from solver.model.domain import (
    ICard,
    CardQP,
    RHADMMSettings,
    CardLogReg,
    RHADMMSolution, NLPSolution
)


class INLPSolver(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def solve(self):
        pass


class LogRegSolver(INLPSolver):

    def __init__(
            self,
            logreg: CardLogReg,
            y: ndarray,
            z: ndarray,
            binvar: ndarray,
            rho: float,
            big_m: float,
            init_x: Optional[ndarray] = None
    ):
        self.model = logreg
        self.y = y
        self.z = z
        self.binvar = binvar
        self.rho = rho
        self.big_m = big_m
        self.x = None
        self.sos_constrs = None
        self.A = zeros((self.model.nvars, self.model.nvars))
        self.rhs = zeros((self.model.nvars,))
        if init_x is not None:
            self.init_x = init_x
        else:
            self.init_x = zeros((self.model.nvars,))

    def _objfcn(self, x: ndarray):
        x = x.reshape(-1, 1)
        return float(self.model.obj_at(x) + self.y.T @ (x - self.z) + (self.rho / 2) * norm(x - self.z, 2) ** 2)

    def _gradfcn(self, x: ndarray):
        x = x.reshape(-1, 1)
        return (self.model.grad_at(x) + self.y + self.rho * (x - self.z)).reshape(-1, )

    def _hessfcn(self, x: ndarray):
        x = x.reshape(-1, )
        return self.model.hess_at(x)

    def _project(self):
        self.x = minimum(self.big_m * self.binvar, maximum(-self.big_m * self.binvar, self.x))

    def _get_sos_data(self):
        for i in range(self.model.nvars):
            if allclose(self.binvar[i], 0):
                self.A[i, i] = 1

    def _set_sos_constrs(self):
        self._get_sos_data()
        self.sos_constrs = LinearConstraint(self.A, self.rhs, self.rhs)

    def _optimize(self):

        # self._set_sos_constrs()
        res = minimize(self._objfcn,
                       self.init_x.reshape(-1,),
                       # jac = self._gradfcn,
                       # method = "trust-constr",
                       # tol = 1e-6,
                       # constraints = self.sos_constrs
                       )
        if res.success:
            self.x = res.x.reshape(-1, 1)
            self._project()
            return NLPSolution(OPTIMAL, self.x, self.model.obj_at(self.x))
        else:
            raise NLPSubSolverError(res.message)

    def solve(self):
        return self._optimize()


class GurobiQPSolver(INLPSolver):

    def __init__(self, qp: CardQP, y: ndarray, z: ndarray, binvar: ndarray, rho: float, big_m: float):
        self.qp = qp
        self.grb_model = gp.Model('qp')
        self.x = self._set_vars(self.qp.nvars)
        self.y = y
        self.z = z
        self.rho = rho
        self.binvar = binvar
        self.big_m = big_m

    def _set_vars(self, n: int):
        return self.grb_model.addMVar(shape = (n,), lb = -GRB.INFINITY)

    def _set_obj(self):

        obj = self.x @ (self.qp.Q * 0.5) @ self.x + \
              self.qp.c.T @ self.x + self.qp.d + self.y.T @ self.x - self.y.T @ self.z + \
              (self.rho / 2) * (self.x @ self.x - 2 * self.z.T @ self.x + self.z.T @ self.z)
        self.grb_model.setObjective(obj, GRB.MINIMIZE)

    def _set_sos_constraints(self):
        for i in range(self.qp.nvars):
            if allclose(self.binvar[i], 0):
                self.grb_model.addConstr(self.x[i] == 0, 'sos_1')

    def _set_big_m_constrs(self):
        self.grb_model.addConstr(self.x <= self.binvar.reshape(-1, ) * self.big_m, "lhs")
        self.grb_model.addConstr(self.x >= - self.binvar.reshape(-1, ) * self.big_m, "rhs")

    def _set_options(self, verbose = False):
        output_flag = 0
        if verbose:
            output_flag = 1

        self.grb_model.setParam('OutputFlag', output_flag)

    def _get_status(self):
        status = self.grb_model.status
        if status is GRB.OPTIMAL:
            return OPTIMAL
        else:
            return INFEASIBLE

    def _create(self):
        self._set_obj()
        self._set_sos_constraints()
        self._set_big_m_constrs()
        self._set_options()

    def _get_vars(self):
        return self.x.X.reshape(-1, 1)

    def _get_objval(self):
        return self.qp.obj_at(self._get_vars())

    def _optimize(self):
        try:
            self.grb_model.optimize()
        except Exception as error:
            print(error)

    def solve(self) -> NLPSolution:
        self._create()
        self._optimize()
        status = self._get_status()
        if status == OPTIMAL:
            return NLPSolution(status, self._get_vars(), self._get_objval())
        else:
            raise NLPSubSolverError("nlp subsolver did not return a solution")


class DistributedPrimalSolver:
    def __init__(
            self,
            mpi_manager: MPIManager,
            model: ICard,
            hot_start_x: Optional[ndarray] = None,
            settings: RHADMMSettings = RHADMMSettings()
    ):
        """

        :param mpi_manager:
        :param model:
        :param settings:
        """
        self.model = model
        self.mpi_manager = mpi_manager
        self.hx = hot_start_x
        self.settings = settings
        self.rank = self.mpi_manager.get_rank()
        self.size = self.mpi_manager.get_size()
        self.x, self.y, self.z, self.z_pre = self._cold_start(self.model.nvars)
        if self.hx is not None:
            self.x = self.hx
        self.rho = None
        self.big_m = None
        self.binvar = None
        self.reduced_z = None
        self.z_pre = None
        self.pres = None
        self.dres = None
        self.t = None
        self.objval = None
        self.fx = None
        self.k = None

    @staticmethod
    def _cold_start(n: int):
        """

        :param n:
        :return:
        """
        return zeros((n, 1)), zeros((n, 1)), zeros((n, 1)), zeros((n, 1))

    def _update_x(self):
        """

        :return:
        """
        if isinstance(self.model, CardQP):
            qp_solver = GurobiQPSolver(self.model, self.y, self.z, self.binvar, self.rho, self.big_m)
            nlp_res = qp_solver.solve()
            self.x = nlp_res.sol
            self.fx = nlp_res.objval
        elif isinstance(self.model, CardLogReg):
            logreg_solver = LogRegSolver(
                self.model,
                self.y,
                self.z,
                self.binvar,
                self.rho,
                self.big_m,
                init_x = self.x
            )
            nlp_res = logreg_solver.solve()
            self.x = nlp_res.sol
            self.fx = nlp_res.objval
        else:
            raise NotRecognizedModel("make sure your model is a qp or logreg")

    def _update_z(self):
        """

        :return:
        """
        self.z_pre = self.z
        local_z = self.x + (1 / self.rho) * self.y
        self.mpi_manager.all_reduce_vec(local_z, self.reduced_z)
        self.z = self.reduced_z / self.size

    def _update_y(self):
        """

        :return:
        """
        self.y += self.rho * (self.x - self.z)

    def _update_rho(self):
        """

        :return:
        """
        mu = AD_MU
        t = AD_T
        if self.t > mu * self.dres:
            self.rho = t * self.rho
        elif self.dres > mu * self.t:
            self.rho = self.rho / t
        else:
            pass

    def _compute_residuals(self):
        """

        :return:
        """
        self.pres = norm(self.x - self.z, 2)
        self.dres = self.rho * self.size ** 0.5 * norm(self.z_pre - self.z, 2)
        self.t = self.mpi_manager.all_reduce(self.pres ** 2)

    def _is_terminated(self) -> bool:
        """

        :return:
        """
        if (self.t <= self.settings.pres) and (self.dres <= self.settings.dres):
            return True
        return False

    def _compute_objval(self):
        """

        :return:
        """
        self.objval = self.mpi_manager.all_reduce(self.fx)

    def _print_info(self):
        """

        :return:
        """
        if self.settings.verbose and self.rank == ROOT:
            print(
                f"iter: {self.k} pres:{self.t:5.8f} dres: {self.dres: 5.8f}"
                f" objval: {self.objval: 5.6f} rho: {self.rho}")

    def _handle_settings(self):
        """

        :return:
        """
        if self.settings.adaptive_rho: #and (not isinstance(self.model, CardLogReg)):
            self._update_rho()

    def _main_loop(self) -> RHADMMSolution:
        """

        :return:
        """

        self.rho = self.settings.rho
        self.reduced_z = zeros((self.model.nvars, 1))
        for self.k in range(self.settings.maxiter):
            self._update_x()
            self._update_z()
            self._update_y()
            self._compute_residuals()
            self._compute_objval()
            self._handle_settings()
            self._print_info()
            if self._is_terminated():
                return RHADMMSolution(self.x, self.fx, self.objval, self.model.grad_at(self.x), OPTIMAL)

        print("maximum number of iteration reached, syscopt provides current solution found so far")
        return RHADMMSolution(self.x, self.fx, self.objval, self.model.grad_at(self.x), MAX_ITER_REACHED)

    def solve(self, binvar: ndarray, big_m: float) -> RHADMMSolution:
        self.binvar = binvar
        self.big_m = big_m
        start = time()
        solution = self._main_loop()
        wtc = time() - start
        solution.wct = wtc
        return solution
