import datetime
import pathlib
from abc import ABC, abstractmethod
from time import time
from typing import List, Optional

from gurobipy.gurobipy import Model, GRB
from mpi4py.MPI import Intercomm
from numpy import (
    ndarray,
    zeros,
    ones,
    array
)
from numpy.linalg import eig

from solver.DIS import *
from solver.algs.distributedprimalsolver import DistributedPrimalSolver
from solver.common import MPIManager
from solver.exeptions import DIPOAError
from solver.model.domain import (
    LinearHyperPlane,
    QuadraticHyperPlane,
    RHADMMSolution,
    DIPOASettings,
    ICard,
    RHADMMSettings,
    MIPSolution,
    Colors,
    CardQP,
    CardLogReg,
    DISCARTSolution,
    DISOASettings
)


class ICardSolver(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def solve(self):
        pass


class CutStorage:
    def __init__(self):
        self._foc: List[List[LinearHyperPlane]] = []
        self._soc: List[List[QuadraticHyperPlane]] = []

    @property
    def foc(self):
        # if not self._foc:
        #     raise DIPOAError("FOC pool is empty")
        return self._foc

    @property
    def soc(self):
        # if not self._soc:
        #     raise DIPOAError("FOC pool is empty")
        return self._soc

    def store_foc(self, cut: List[LinearHyperPlane]):
        """

        :param cut:
        :return:
        """
        self._foc.append(cut)

    def store_soc(self, cut: List[QuadraticHyperPlane]):
        """

        :param cut:
        :return:
        """
        self._soc.append(cut)

    def __str__(self):
        return f"{self._foc}"


class IMultipleTreeMIPSolver(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def solve(self):
        pass


class ISingleTreeMIPSolver(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def solve(self) -> DISCARTSolution:
        pass

    @abstractmethod
    def gen_cuts(self, storage: CutStorage):
        pass

    @abstractmethod
    def gen_hyb_cuts(self, storage: CutStorage):
        pass

    @abstractmethod
    def set_big_m_constrs(self):
        pass

    @abstractmethod
    def set_sos_constrs(self):
        pass

    @abstractmethod
    def set_card_constr(self):
        pass


class GurobiDIPOA(IMultipleTreeMIPSolver):

    def __init__(
            self,
            mpi_manager: MPIManager,
            model: ICard,
            storage: CutStorage,
            settings: DIPOASettings = DIPOASettings()
    ):
        """

        :param mpi_manager:
        :param model:
        :param storage:
        :param settings:
        """
        self.mpi_manager = mpi_manager
        self.rank = self.mpi_manager.get_rank()
        self.size = self.mpi_manager.get_size()
        self.grb_model = Model()
        self.model = model
        self.storage = storage
        self.n = self.model.nvars
        self.settings = settings
        self.alpha = None
        self.x = None
        self.delta = None
        self.s = None
        self.objval = None

    def _set_vars(self):
        self.alpha = self.grb_model.addMVar(shape = (self.size,), lb = -GRB.INFINITY)
        self.x = self.grb_model.addMVar(shape = (self.n,), lb = -GRB.INFINITY)
        self.delta = self.grb_model.addMVar(shape = (self.n,), vtype = GRB.BINARY)
        self.s = self.grb_model.addMVar(shape = (self.n,), vtype = GRB.BINARY)

    def _set_obj(self):
        obj = ones((self.size, 1)).T @ self.alpha
        self.grb_model.setObjective(obj, GRB.MINIMIZE)

    def _add_linear_approx(self, index: int, cut: LinearHyperPlane):
        """

        :param index:
        :param cut:
        :return:
        """
        self.grb_model.addConstr(
            self.alpha[index] >= cut.fx + cut.gfx.T @ self.x - float(cut.gfx.T @ cut.x),
            name = f"{index}-foc"
        )

    def _add_quadratic_approx(self, index: int, cut: QuadraticHyperPlane):
        """

        :param index:
        :param cut:
        :return:
        """
        quad_term = cut.eig / 2 * (self.x @ self.x - 2 * cut.x.T @ self.x + cut.x.T @ cut.x)
        self.grb_model.addConstr(
            self.alpha[index] >= cut.fx + cut.gfx.T @ self.x - cut.gfx.T @ cut.x + quad_term,
            name = f"{index}-soc"
        )

    def _set_loa_constrs(self):
        if self.storage.foc:  # add foc constrs
            for cuts in self.storage.foc:
                for cut_index, cut in enumerate(cuts):
                    self._add_linear_approx(cut_index, cut)
        # else:
        #     raise DIPOAError("no linear approximation found")

    def _set_qoa_constrs(self):
        if self.storage.soc:
            for cuts in self.storage.soc:
                for cut_index, cut in enumerate(cuts):
                    self._add_quadratic_approx(cut_index, cut)

    def _set_big_m_constrs(self):
        self.grb_model.addConstr(self.x <= self.settings.big_m * self.delta, name = f'bigml')
        self.grb_model.addConstr(-self.settings.big_m * self.delta <= self.x, name = f'bigmr')

    def _set_sos_constrs(self):
        self.grb_model.addConstr(self.x <= self.settings.big_m, name = f'cardp')
        self.grb_model.addConstr(-self.settings.big_m <= self.x, name = f'cardn')
        xlist = self.x.tolist()
        slist = self.s.tolist()
        self.grb_model.addConstr(self.s + self.delta == 1.0, "auxsos")
        for i in range(self.n):
            self.grb_model.addSOS(GRB.SOS_TYPE1, [slist[i], xlist[i]], [1, 1])

    def _set_card_constrs(self):
        self.grb_model.addConstr(self.delta.sum() <= self.model.nzeros, name = 'd')

    def _set_gurobi_settings(self, verbose: int = 0):
        """

        :param verbose:
        :return:
        """
        self.grb_model.setParam('OutputFlag', verbose)

    def _optimize(self):
        try:
            self.grb_model.optimize()
        except Exception as error:
            print(error)

    def _create_model(self):
        self._set_vars()
        self._set_obj()
        self._set_loa_constrs()
        self._set_big_m_constrs()
        self._set_card_constrs()
        if self.settings.soc:
            self._set_qoa_constrs()
        if self.settings.sos:
            self._set_sos_constrs()

    def _get_status(self):
        status = self.grb_model.status
        if status is GRB.OPTIMAL:
            return OPTIMAL
        else:
            return INFEASIBLE

    def _get_vars(self):
        self.delta = self.delta.X.reshape(self.n, 1)
        self.x = self.x.X.reshape(self.n, 1)

    def _get_objval(self):
        self.objval = self.grb_model.objVal

    def solve(self) -> MIPSolution:
        self._create_model()
        self._set_gurobi_settings()
        start = time()
        self._optimize()
        wct = time() - start
        status = self._get_status()
        if status == OPTIMAL:
            self._get_vars()
            self._get_objval()
            return MIPSolution(
                binvar = self.delta,
                x = self.x,
                objval = self.objval,
                wct = wct,
                status = status
            )
        else:
            raise DIPOAError("MIP Solver did not provide a solution")


class GurobiSingleTree(ISingleTreeMIPSolver):

    def __init__(
            self,
            mpi_manager: MPIManager,
            model: ICard,
            init_binary: ndarray,
            settings: DISOASettings
    ):
        """

        :param mpi_manager:
        :param model:
        :param init_binary:
        :param settings:
        """
        self.mpi_manager = mpi_manager
        self.model = model
        self.size = self.mpi_manager.get_size()
        self.rank = self.mpi_manager.get_rank()
        self.binvar = init_binary
        self.settings = settings
        self.grb_model = Model('single-tree')
        self.alpha = None
        self.x = None
        self.delta = None
        self.s = None
        self.cb_alpha = None
        self.cb_x = None
        self.vars_list = []
        self.incumbent: Optional[ndarray] = None
        self.binvar = init_binary
        self.nlp_solution: Optional[RHADMMSolution] = None
        self.rcv_gx: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_x: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_fx: Optional[List[float]] = None
        self.lazy_model = None
        self._set_vars()
        self._set_obj()
        self._aug_vars()
        self.manager: MIPManager = MIPManager(self.size)
        self.ub = DIPOA_UB

    def set_big_m_constrs(self):

        for i in range(self.model.nvars):
            self.grb_model.addConstr(self.x[i, 0] <= self.settings.big_m * self.delta[i, 0], name = f'cardp_{i}')
            self.grb_model.addConstr(- self.settings.big_m * self.delta[i, 0] <= self.x[i, 0], name = f'cardn_{i}')

    def set_sos_constrs(self):
        for i in range(self.model.nvars):
            self.grb_model.addConstr(self.x[i, 0] <= self.settings.big_m, name = f'cardp')
            self.grb_model.addConstr(-self.settings.big_m <= self.x[i, 0], name = f'cardn')
            self.grb_model.addConstr(self.s[i, 0] + self.delta[i, 0] == 1.0, "auxsos")
            self.grb_model.addSOS(GRB.SOS_TYPE1, [self.s[i, 0], self.x[i, 0]], [1, 1])

    def set_card_constr(self):
        self.grb_model.addConstr(self.delta.sum() <= self.model.nzeros, name = 'bin-constr')

    def gen_hyb_cuts(self, storage: CutStorage):
        """

        :param storage:
        :return:
        """

        for cuts in storage.soc:
            for index, cut in enumerate(cuts):
                self._add_qoa_cut(index, cut, self.grb_model)

    def gen_cuts(self, storage: CutStorage):
        for cuts in storage.foc:
            for index, cut in enumerate(cuts):
                self._add_loa_cut(index, cut, self.grb_model)

    def _set_vars(self):
        self.alpha = self.grb_model.addVars(self.size, 1, lb = - GRB.INFINITY)
        self.x = self.grb_model.addVars(self.model.nvars, 1, lb = - GRB.INFINITY)
        self.delta = self.grb_model.addVars(self.model.nvars, 1, vtype = GRB.BINARY)
        self.s = self.grb_model.addVars(self.model.nvars, 1, vtype = GRB.BINARY)

    def _set_obj(self):
        obj = 0
        for i in range(self.size):
            obj += self.alpha[i, 0]
        self.grb_model.setObjective(obj, GRB.MINIMIZE)

    def _add_loa_cut(self, index: int, cut: LinearHyperPlane, model: Model):
        """

        :param index:
        :param cut:
        :param model:
        :return:
        """

        grb_sum = sum([float(cut.gfx[k]) * self.x[k, 0] for k in range(self.model.nvars)])

        model.addConstr(
            self.alpha[index, 0] >= cut.fx + grb_sum - float(cut.gfx.T @ cut.x),
            name = f'cut_{index}'
        )

    def _add_qoa_cut(self, index: int, cut: QuadraticHyperPlane, model: Model):

        grb_sum = sum([float(cut.gfx[k]) * self.x[k, 0] for k in range(self.model.nvars)])
        quadratic_term = sum([self.x[k, 0] ** 2 for k in range(self.model.nvars)]) - 2 * sum(
            [self.x[k, 0] * cut.x[k] for k in range(self.model.nvars)]) + cut.x.T @ cut.x
        model.addConstr(
            self.alpha[index, 0] >= cut.fx + grb_sum - float(cut.gfx.T @ cut.x) + 0.5 * cut.eig * quadratic_term,
            name = f'cut_{index}'
        )

    def _aug_vars(self):

        for i in range(self.size):
            self.vars_list.append(self.alpha[i, 0])
        for i in range(self.model.nvars):
            self.vars_list.append(self.x[i, 0])
        for i in range(self.model.nvars):
            self.vars_list.append(self.delta[i, 0])

    def _get_incumbent(self, model: Model):
        """

        :param model:
        :return:
        """

        incumbent = array(model.cbGetSolution(model._vars)).reshape(-1, 1)
        self.binvar = incumbent[self.size + self.model.nvars: self.size + 2 * self.model.nvars]

    def _solve_primal(self):
        primal_solver = DistributedPrimalSolver(self.mpi_manager, model = self.model)
        self.nlp_solution = primal_solver.solve(self.binvar, self.settings.big_m)
        self.ub = min(self.ub, self.nlp_solution.tfx)

    def _get_grb_cb_vars(self, model: Model):
        """

        :param model:
        :return:
        """

        self.cb_alpha = model._vars[0:self.size]
        self.cb_x = model._vars[self.size: self.size + self.model.nvars]

    def _all_gather_cut_info(self):

        self.rcv_fx = self.mpi_manager.all_gather(self.nlp_solution.fx)
        self.mpi_manager.all_gather_vec(self.nlp_solution.gx, self.rcv_gx)
        self.mpi_manager.all_gather_vec(self.nlp_solution.x, self.rcv_x)

    def _add_lazy_oa_cut(self, index: int, cut: LinearHyperPlane):
        """

        :param index:
        :param cut:
        :return:
        """

        lazy_sum = sum([cut.gfx[k][0] * self.cb_x[k] for k in range(self.model.nvars)])
        self.grb_model.cbLazy(
            self.cb_alpha[index] >= cut.fx + lazy_sum - float(cut.gfx.T @ cut.x)
        )

    def _add_lazy_oa_cuts(self):
        self._all_gather_cut_info()
        for lazy_index in range(self.size):
            lazy_cut = LinearHyperPlane(
                x = self.rcv_x[lazy_index, :].reshape(-1, 1),
                fx = self.rcv_fx[lazy_index],
                gfx = self.rcv_gx[lazy_index, :].reshape(-1, 1)
            )
            self._add_lazy_oa_cut(lazy_index, lazy_cut)

    def _optimize(self):
        def distributed_callback(lazy_model: Model, where: int):
            """

            :param lazy_model:
            :param where:
            :return:
            """

            if where == GRB.Callback.MIPSOL:
                self._get_incumbent(lazy_model)
                self._solve_primal()
                self.manager.update_num_lazy_constrs()
                self.manager.update_total_nlp_time(self.nlp_solution.wct)
                self._get_grb_cb_vars(lazy_model)
                self._add_lazy_oa_cuts()

        self.grb_model._vars = self.vars_list
        self.grb_model.Params.lazyConstraints = 1
        self._apply_settings()
        self.grb_model.optimize(distributed_callback)

    def _get_vars(self):
        sol_vec = zeros((self.size + 3 * self.model.nvars, 1))
        for j, v in enumerate(self.grb_model.getVars()):
            sol_vec[j] = v.x
        self.binvar = sol_vec[self.size + self.model.nvars: self.size + 2 * self.model.nvars]
        self._solve_primal()

    def _get_status(self):
        if self.grb_model.status == GRB.OPTIMAL:
            return 0
        else:
            return 1

    def _apply_settings(self):
        if self.rank == ROOT_NODE:
            self.grb_model.setParam('OutputFlag', self.settings.verbose)
        else:
            self.grb_model.setParam('OutputFlag', 0)
        self.grb_model.setParam('MIPGap', 1e-2)
        self.grb_model.setParam('MIPGapAbs', 1e-2)
        self.grb_model.setParam('MIPFocus', 1)
        self.grb_model.setParam('NodeMethod', 1)
        self.grb_model.setParam('CutPasses', 100)
        self.grb_model.setParam('GomoryPasses', 100)
        self.grb_model.setParam('Threads', 1)

    def solve(self):

        self._optimize()
        status = self._get_status()
        self._get_vars()
        return DISCARTSolution(
            x = self.nlp_solution.x,
            objval = self.ub,
            status = status,
            num_lazy_constrs = self.manager.num_lazy_constrs,
            total_nlp_time = self.manager.total_nlp_time
        )


class CutGenerator:
    def __init__(self, mpi_manager: MPIManager, storage: CutStorage):
        """

        :param mpi_manager:
        :param storage:
        """
        self._mpi_manager = mpi_manager
        self._soc: Optional[QuadraticHyperPlane] = None
        self._foc: Optional[LinearHyperPlane] = None
        self._storage = storage
        self.rcv_fx: Optional[List] = None
        self.rcv_x: Optional[ndarray] = None
        self.rcv_gfx: Optional[ndarray] = None
        self.rcv_eig: Optional[List] = None

    @property
    def soc(self):
        return self._soc

    @property
    def foc(self):
        return self._foc

    def _init_rcvs(self, n: int):
        if self._mpi_manager.get_rank() == ROOT_NODE:
            self.rcv_x = zeros((self._mpi_manager.get_size(), n))
            self.rcv_gfx = zeros((self._mpi_manager.get_size(), n))
            self.rcv_fx = []
        else:
            self.rcv_x = None
            self.rcv_gfx = None
            self.rcv_fx = None

    def _init_rcvs_hybrid(self, n: int):
        self.rcv_x = zeros((self._mpi_manager.get_size(), n))
        self.rcv_gfx = zeros((self._mpi_manager.get_size(), n))
        self.rcv_fx = []
        self.rcv_eig = []

    def _distributed_cut_info(self, prime_info: RHADMMSolution):
        """

        :param prime_info:
        :return:
        """
        self.n = prime_info.x.shape[0]  # nvars
        self._init_rcvs(self.n)
        self.rcv_fx = self._mpi_manager.gather(prime_info.fx)
        self._mpi_manager.gather_vec(prime_info.x, self.rcv_x)
        self._mpi_manager.gather_vec(prime_info.gx, self.rcv_gfx)

    def _distributed_hybrid_cut_info(self, prime_info: RHADMMSolution, min_eig: float):
        """

        :param prime_info:
        :param min_eig:
        :return:
        """
        self.n = prime_info.x.shape[0]  # nvars
        self._init_rcvs_hybrid(self.n)
        self.rcv_fx = self._mpi_manager.all_gather(prime_info.fx)
        self.rcv_eig = self._mpi_manager.all_gather(min_eig)
        self._mpi_manager.all_gather_vec(prime_info.x, self.rcv_x)
        self._mpi_manager.all_gather_vec(prime_info.gx, self.rcv_gfx)

    def gen_focs(self, prime_info: RHADMMSolution):
        """

        :param prime_info:
        :return:
        """
        self._distributed_cut_info(prime_info)

        if self._mpi_manager.get_rank() == ROOT_NODE:
            current_apprxs: List[LinearHyperPlane] = []
            for node in range(self._mpi_manager.get_size()):
                lhp = LinearHyperPlane(
                    fx = self.rcv_fx[node],
                    x = self.rcv_x[node, :].reshape(self.n, 1),
                    gfx = self.rcv_gfx[node, :].reshape(self.n, 1)
                )
                current_apprxs.append(lhp)
            self._storage.store_foc(current_apprxs)

    def gen_soc(self, prime_info: RHADMMSolution, eig_val: float, hybrid: bool):
        """

        :param prime_info:
        :param eig_val:
        :param hybrid:
        :return:
        """

        if hybrid:
            self._distributed_hybrid_cut_info(prime_info, min_eig = eig_val)
            current_apprxs: List[QuadraticHyperPlane] = []
            for node in range(self._mpi_manager.get_size()):
                qhp = QuadraticHyperPlane(
                    fx = self.rcv_fx[node],
                    x = self.rcv_x[node, :].reshape(self.n, 1),
                    gfx = self.rcv_gfx[node, :].reshape(self.n, 1),
                    eig = eig_val
                )
                current_apprxs.append(qhp)
            self._storage.store_soc(current_apprxs)
        else:
            self._distributed_cut_info(prime_info)
            if self._mpi_manager.get_rank() == ROOT_NODE:
                current_apprxs: List[QuadraticHyperPlane] = []
                for node in range(self._mpi_manager.get_size()):
                    qhp = QuadraticHyperPlane(
                        fx = self.rcv_fx[node],
                        x = self.rcv_x[node, :].reshape(self.n, 1),
                        gfx = self.rcv_gfx[node, :].reshape(self.n, 1),
                        eig = eig_val
                    )
                    current_apprxs.append(qhp)
                self._storage.store_soc(current_apprxs)


class MIPManager:
    def __init__(self, mpi_size: int):
        self._num_lazy_constrs = 0
        self._size = mpi_size
        self._total_nlp_time = 0

    @property
    def num_lazy_constrs(self):
        return self._num_lazy_constrs

    def update_num_lazy_constrs(self):
        self._num_lazy_constrs += self._size

    @property
    def total_nlp_time(self):
        return self._total_nlp_time

    def update_total_nlp_time(self, value: float):
        self._total_nlp_time += value


class DIPOAManager:
    def __init__(self, mpi_manager: MPIManager, settings: DIPOASettings = DIPOASettings()):
        """

        :param mpi_manager:
        :param settings:
        """
        self._ub = DISCART_INF
        self._lb = - self._ub
        self._gap_array = []
        self._mpi_manager = mpi_manager
        self._size = self._mpi_manager.get_size()
        self._rank = self._mpi_manager.get_rank()
        self._settings = settings
        self.abs_gap = self._ub - self._lb
        self.maxiter: Optional[int] = None
        self._num_foc: int = 0
        self._num_soc: int = 0
        self._total_nlp_time: int = 0
        self._total_mip_time: int = 0
        self._num_lazy_constrs: int = 0
        self._num_hybrid_soc: int = 0

    @property
    def gap_array(self):
        return self._gap_array

    @property
    def lb(self):
        return self._lb

    @property
    def ub(self):
        return self._ub

    def update_lb(self, lb: float):
        self._lb = lb

    def update_ub(self, ub: float):
        self._ub = min(ub, self._ub)

    def _update_abs_gap(self):
        self.abs_gap = self._ub - self._lb
        self.abs_gap = self._mpi_manager.bcast(self.abs_gap)
        self._gap_array.append(self.abs_gap)

    def is_terminated(self) -> bool:
        self._update_abs_gap()
        if self.abs_gap <= self._settings.rgap:
            return True
        else:
            return False

    @property
    def num_foc(self):
        return self._num_foc

    @property
    def num_soc(self):
        return self._num_soc

    def update_num_foc(self):
        self._num_foc += self._size

    def update_num_soc(self):
        self._num_soc += self._size

    def update_num_lazy_constr(self):
        self._num_lazy_constrs += self._size

    def update_num_hybrid_soc(self):
        self._num_hybrid_soc += self._size

    @property
    def num_hybrid_soc(self):
        return self._num_hybrid_soc

    @property
    def total_nlp_time(self):
        return self._total_nlp_time

    @total_nlp_time.setter
    def total_nlp_time(self, value: float):
        """

        :param value:
        :return:
        """
        self._total_nlp_time = value

    @property
    def total_mip_time(self):
        return self._total_mip_time

    @total_mip_time.setter
    def total_mip_time(self, value: float):
        """

        :param value:
        :return:
        """
        self._total_mip_time = value

    def is_event_triggerd(self):
        if len(self._gap_array) >= INITIAL_ITER:
            current_diff = self._gap_array[-2] - self._gap_array[-1]
            if current_diff <= EVENT_GAP:
                return True
            else:
                return False
        return False


class DIPOA(ICardSolver):

    def __init__(self, comm: Intercomm, model: ICard, settings: DIPOASettings = DIPOASettings()):
        """

        :param comm:
        :param model:
        :param settings:
        """
        self.k = 0
        self.model = model
        self.settings = settings
        self.mpi_manager = MPIManager(comm)
        self.rank = self.mpi_manager.get_rank()
        self.size = self.mpi_manager.get_size()
        self.primal_settings = RHADMMSettings()
        self.binvar = zeros((self.model.nvars, 1))
        self.nlp_solution: Optional[RHADMMSolution] = None
        self.mip_solution: Optional[MIPSolution] = None
        self.cut_manager: CutStorage = CutStorage()
        self.cut_generator: CutGenerator = CutGenerator(self.mpi_manager, self.cut_manager)
        self.dipoa_manager: DIPOAManager = DIPOAManager(self.mpi_manager, self.settings)
        self.flag = True
        self.colors = Colors()
        self.iter_time = None
        self.rcv_x: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_gx: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_fx: Optional[List[float]] = None
        self.rcv_eig: Optional[List[float]] = None
        self.solver_info: str = ''
        self.header: str = ''
        self.time_stamp: str = ""
        self.hot_x: Optional[ndarray] = None

    def _print_header(self):
        self.header = f"{'iter':4s}| {'lb':10s}| {'ub':10s}| {'gap':10s}| " \
                      f"{'nlp-time':10s}| {'mip-time':10s}| {'iter-time':10s} {'soc':4s} {'sos':4s}"
        print(self.header)

    def _write_to_file(self, header = False):
        """

        :param header:
        :return:
        """
        if self.k == 0:
            self.time_stamp = str(datetime.datetime.now()).split('.')[0].replace(' ', '_')

        target_directory = WORKING_DIR
        pathlib.Path(target_directory + '/' + LOGS).mkdir(exist_ok = True)

        target_file = os.path.join(target_directory, LOGS, f"log_{self.time_stamp}.txt")
        with open(target_file, 'a') as writer:
            if not header:
                writer.write(self.solver_info + '\n')
            else:
                writer.write(self.header + '\n')

    def _print_info(self):
        self.solver_info = f"{self.k: 3d} {self.dipoa_manager.lb:10.8f} {self.dipoa_manager.ub:10.8f} " \
                           f"{self.dipoa_manager.ub - self.dipoa_manager.lb:10.5f} {self.nlp_solution.wct:10.5f} " \
                           f"{self.mip_solution.wct:10.5f} {self.iter_time:10.5f}" \
                           f" {self.settings.soc:7b} {self.settings.sos:7b}"

        if self.model.nvars <= ITER_COUNT:
            count = 1
        else:
            count = 10

        if self.k % count == 0:
            print(self.solver_info)

    def _solve_primal(self):
        if self.hot_x is not None:
            primal_solver = DistributedPrimalSolver(
                self.mpi_manager,
                model = self.model,
                settings = self.primal_settings,
                hot_start_x = self.hot_x
            )
        else:
            primal_solver = DistributedPrimalSolver(
                self.mpi_manager,
                model = self.model,
                settings = self.primal_settings,
            )

        self.nlp_solution = primal_solver.solve(self.binvar, self.settings.big_m)
        self.hot_x = self.nlp_solution.x

    def _solve_master(self):
        if self.rank == ROOT_NODE:
            mip_solver = GurobiDIPOA(self.mpi_manager, self.model, self.cut_manager, self.settings)
            self.mip_solution = mip_solver.solve()
            self.binvar = self.mip_solution.binvar
        self.mpi_manager.bcast_vec(self.binvar)

    def _update_bounds(self):
        if self.rank == ROOT_NODE:
            self.dipoa_manager.update_lb(self.mip_solution.objval)
            self.dipoa_manager.update_ub(self.nlp_solution.tfx)

    def _generate_approximations(self, hybrid: bool):
        """

        :param hybrid:
        :return:
        """
        if self.settings.soc:
            min_eig = self._compute_min_eig()
            if hybrid:
                self.dipoa_manager.update_num_hybrid_soc()
            self.cut_generator.gen_soc(self.nlp_solution, eig_val = min_eig, hybrid = hybrid)
            self.dipoa_manager.update_num_soc()
        else:
            self.cut_generator.gen_focs(self.nlp_solution)
            self.dipoa_manager.update_num_foc()

    def _compute_min_eig(self):
        if isinstance(self.model, CardQP):
            m = min(eig(self.model.Q)[0])
            assert m > 0, "m must be positive"
            return m
        elif isinstance(self.model, CardLogReg):
            m = min(eig(self.model.hess_at(self.nlp_solution.x))[0])
            assert m > 0, "m must be positive"
            return m

    def _update_settings(self):
        self.settings.soc = True
        if self.rank == ROOT_NODE:
            print(
                f"{self.colors.WARNING}Warning: second order cut "
                f"generation activated {self.colors.ENDC}")

    def _apply_settings(self):
        if self.settings.verbose and self.rank == ROOT_NODE:
            if self.k == 0:
                self._print_header()
                self._write_to_file(header = True)
            else:
                self._print_info()
                self._write_to_file()

    def _apply_hybrid_mode(self):
        if len(self.dipoa_manager.gap_array) >= 2 and \
                (self.dipoa_manager.gap_array[-2] - self.dipoa_manager.gap_array[-1] <= HYBRID_GAP):
            print(self.colors.WARNING, f"hybrid mode is activated at iteration {self.k}"
                                       f" with gap "
                                       f"{self.dipoa_manager.gap_array[-2] - self.dipoa_manager.gap_array[-1]}",
                  self.colors.ENDC)
            return DISOA(self.mpi_manager.comm, self.model).solve()

    def _main_loop(self) -> DISCARTSolution:
        for self.k in range(self.settings.maxiter):
            iter_time = time()
            self._solve_primal()
            if self.settings.hybrid and self.settings.soc:
                hybrid_results = self._apply_hybrid_mode()
                if hybrid_results:
                    return hybrid_results
            self._generate_approximations(self.settings.hybrid)
            self._solve_master()
            if self.rank == ROOT_NODE:
                self.dipoa_manager.total_mip_time += self.mip_solution.wct
                self.dipoa_manager.total_nlp_time += self.nlp_solution.wct
            self._update_bounds()
            self._apply_settings()
            if self.dipoa_manager.is_terminated():
                if self.rank == ROOT_NODE:
                    return DISCARTSolution(
                        x = self.nlp_solution.x,
                        objval = self.nlp_solution.tfx,
                        status = 0,
                        maxiter = self.k,
                        total_mip_time = self.dipoa_manager.total_mip_time,
                        total_nlp_time = self.dipoa_manager.total_nlp_time,
                        num_foc = self.dipoa_manager.num_foc,
                        num_soc = self.dipoa_manager.num_soc,
                        num_hybrid_soc = self.dipoa_manager.num_hybrid_soc,
                        algorithm = self.__class__.__name__,
                        model = self.model.__class__.__name__
                    )
                else:
                    return DISCARTSolution()
            else:
                if self.dipoa_manager.is_event_triggerd() and self.flag:
                    self._update_settings()
                    self.flag = False
            self.iter_time = time() - iter_time
        print("Maximum number of iteration reached. current solution provided")
        if self.rank == ROOT_NODE:
            return DISCARTSolution(
                x = self.nlp_solution.x,
                objval = self.nlp_solution.tfx,
                status = 0,
                maxiter = self.k,
                total_mip_time = self.dipoa_manager.total_mip_time,
                total_nlp_time = self.dipoa_manager.total_nlp_time,
                num_foc = self.dipoa_manager.num_foc,
                num_soc = self.dipoa_manager.num_soc,
                num_hybrid_soc = self.dipoa_manager.num_hybrid_soc,
                algorithm = self.__class__.__name__
            )
        else:
            return DISCARTSolution()

    def solve(self):
        start = time()
        res = self._main_loop()
        wct = time() - start
        res.wct = wct
        return res


class DISOA(ICardSolver):
    def __init__(
            self,
            comm: Intercomm,
            model: ICard,
            settings: DISOASettings = DISOASettings(),
            hybrid_pool: Optional[CutStorage] = None
    ):
        """

        :param comm:
        :param model:
        :param settings:
        :param hybrid_pool:
        """
        self.mpi_manager = MPIManager(comm)
        self.size = self.mpi_manager.get_size()
        self.rank = self.mpi_manager.get_rank()
        self.model = model
        self.settings = settings
        self.hybrid = hybrid_pool
        self.primal_settings = RHADMMSettings()
        self.binvar = zeros((self.model.nvars, 1))
        self.nlp_solution: Optional[RHADMMSolution] = None
        self.storage = CutStorage()
        self.rcv_x: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_gx: ndarray = zeros((self.size, self.model.nvars))
        self.rcv_fx: Optional[List[float]] = None
        self.mip_solver: Optional[ISingleTreeMIPSolver] = GurobiSingleTree(
            self.mpi_manager,
            self.model,
            self.binvar,
            self.settings
        )
        self.ub = DIPOA_UB

    def _solve_initial_primal(self):
        primal_solver = DistributedPrimalSolver(self.mpi_manager, model = self.model, settings = self.primal_settings)
        self.nlp_solution = primal_solver.solve(self.binvar, self.settings.big_m)
        self._get_initial_cut_info()

    def _get_initial_cut_info(self):
        self.mpi_manager.all_gather_vec(self.nlp_solution.x, self.rcv_x)
        self.mpi_manager.all_gather_vec(self.nlp_solution.gx, self.rcv_gx)
        self.rcv_fx = self.mpi_manager.all_gather(self.nlp_solution.fx)

    def _create_initial_cuts(self):
        pool = []
        for i in range(self.size):
            cut = LinearHyperPlane(
                x = self.rcv_x[i, :],
                fx = self.rcv_fx[i],
                gfx = self.rcv_gx[i, :]
            )
            pool.append(cut)
        self.storage.store_foc(pool)

    def _generate_initial_oa_cuts(self):
        self.mip_solver.gen_cuts(self.storage)

    def _generate_hybrid_oa_cuts(self):
        self.mip_solver.gen_hyb_cuts(self.hybrid)

    def _add_big_m_constrs(self):
        self.mip_solver.set_big_m_constrs()

    def _add_sos_constrs(self):
        self.mip_solver.set_sos_constrs()

    def _add_card_constr(self):
        self.mip_solver.set_card_constr()

    def _optimize(self):
        if not self.hybrid:
            self._solve_initial_primal()
            self._create_initial_cuts()
            self._generate_initial_oa_cuts()
            self._add_big_m_constrs()
            self._add_card_constr()
            if self.settings.sos:
                self._add_sos_constrs()
            return self.mip_solver.solve()
        else:
            self._generate_hybrid_oa_cuts()
            self._add_big_m_constrs()
            self._add_card_constr()
            if self.settings.sos:
                self._add_sos_constrs()
            return self.mip_solver.solve()

    def solve(self):
        start = time()
        results = self._optimize()
        wct = time() - start
        results.algorithm = self.__class__.__name__
        results.model = self.model.__class__.__name__
        results.wct = wct
        return results


class DIHOA(DIPOA):
    def solve(self):
        self.settings.hybrid = True
        self.settings.soc = True
        start = time()
        result = self._main_loop()
        wct = time() - start
        result.wct = wct
        return result
