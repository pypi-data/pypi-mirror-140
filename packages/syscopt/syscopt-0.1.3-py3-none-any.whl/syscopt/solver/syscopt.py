"""SysCopt: System of cardinality optimization.

SysCopt is a Python framework designed to solve Distributed Cardinality Constrained Optimization (DCCO) problems
over peer-to-peer networks of computing nodes.

SysCopt consists of three distributed algorithms to solve DCCO problems whereby an iteration procedure is applied by
each node of the network which alternates communication and computation phases until a solution is found.

SysCopt provides the following distributed algorithms:
    - Distributed Primal Outer Approximation (DiPOA)
    - Distributed Single-Tree Outer Approximation (DiSOA)
    - Distributed Hybrid Outer Approximation (DIHOA).

SysCopt was developed by Alireza Olama at the Federal University of Santa Catarina (UFSC) in the research gorup of
Prof. Eduardo Camponogara

email: alireza.lm69@gmail.com
github: https://github.com/alirezalm
"""
import os
import sys
from typing import Optional, Any

from solver.DIS import *
from solver.algs.solver import ICardSolver, DIPOA, DISOA, DIHOA
from solver.common import file_handler
from solver.exeptions import ModelingError
from solver.model.domain import (
    CardQP,
    CardLogReg,
    ICard,
    DISCARTSolution
)
from solver.model.parsers import (
    CQPInputParser,
    HeaderParser,
    CLogRegInputParser,
    IParser,
    SettingParser,
    write_solution
)
from solver.model.validators import (
    CardQPValidator,
    CardLogRegValidator,
    IValidator, SettingsValidator
)


class SysCopt(object):
    def __init__(
            self,
            comm: Any,
            input_file: str,
            settings_file: str
    ):
        """

        :param comm: MPI communicator
        :param input_file: path to input file
        :param settings_file: path to output file
        """
        self.comm = comm
        self.fname = input_file
        self._system_check()
        self.settings_file = settings_file  # subject to change -> read from jsonfile
        self.pdate, self.pname = self._indicate_problem_type()

        self.input_parser: IParser = self._get_parser()
        self.settings_parser: SettingParser = SettingParser(self.settings_file)
        self.settings = self.settings_parser.parse()

        self.model: ICard = self.input_parser.parse()
        self.model_validator: IValidator = self._get_validator()
        self.setting_validator: SettingsValidator = SettingsValidator(self.settings)
        self._is_valid()
        self.solver: ICardSolver = self._get_solver()
        if self.comm.Get_rank() == ROOT_NODE:
            self._print_header()
        self.result: Optional[DISCARTSolution] = None

    def _indicate_problem_type(self):
        hp = HeaderParser(self.fname, self.comm.Get_rank())
        try:
            return hp.parse()
        except ModelingError as error:
            print(error)
            self.comm.Abort()

    def _get_parser(self) -> IParser:
        if "qp" in self.pname:
            return CQPInputParser(self.fname, self.comm.Get_rank())
        return CLogRegInputParser(self.fname, self.comm.Get_rank())

    def _get_validator(self) -> IValidator:
        if "qp" in self.pname:
            assert isinstance(self.model, CardQP), "model must be QP"
            return CardQPValidator(self.model)
        assert isinstance(self.model, CardLogReg), "model must be logreg"
        return CardLogRegValidator(self.model)

    def _is_valid(self):
        if self.model_validator.is_valid():
            self.model_validator.show_valid_msg()
        if self.setting_validator.is_valid():
            self.setting_validator.show_valid_msg()

    def _get_solver(self) -> ICardSolver:
        if self.settings.algorithm == 0:
            return DIPOA(comm = self.comm, model = self.model, settings = self.settings.dipoa_opts)
        elif self.settings.algorithm == 1:
            return DISOA(comm = self.comm, model = self.model, settings = self.settings.disoa_opts)
        else:
            return DIHOA(comm = self.comm, model = self.model, settings = self.settings.dipoa_opts)

    @staticmethod
    def get_version():
        return "0.1.0"

    @staticmethod
    def _get_platform():
        return sys.platform

    @staticmethod
    def _system_check():
        grb = os.environ.get("GUROBI_HOME", "")
        if not grb:
            raise ModelingError("Make sure Gurobi is installed and GUROBI_HOME is set as env var")

    def _print_header(self):
        header = \
            f"""
                                       SYSCOPT  -   SYSTEM OF CARDINALITY OPTIMIZATION    (c) Alireza Olama   
                                       
                                       Federal University of Santa Catarina  ---  UFSC

                                       current version: {self.get_version()}
                                        
                                       running platform: {self._get_platform()}
                                        
                                       github: {GITHUB}

                                       email: {EMAIL}
                   """
        print(header)
        print(
            "SysCopt is a Python framework designed to solve Distributed Cardinality Constrained Optimization (DCCO)\n"
            "problems over peer-to-peer networks of computing nodes.SysCopt consists of three distributed algorithms\n"
            "to solve DCCO problems whereby an iteration procedure is applied byeach node of the network which \n"
            "alternates communication and computation phases until a solution is found.\n")

        print(
            f"Python Version: {sys.version}"
        )
        print(
            f"python executable: {sys.executable}"
        )
        for i in range(self.comm.Get_size()):
            print(
                f"input file {i}: {file_handler(self.fname, i)}"
            )
        if POSTFIX not in self.settings_file:
            print(
                f"settings file: {self.settings_file}" + POSTFIX
            )
        else:
            print(
                f"settings file: {self.settings_file}"
            )
        if isinstance(self.model, CardQP):
            print(
                f"Model = {self.model.__class__.__name__}"
            )
        else:
            print(
                f"Model = {self.model.__class__.__name__}"
            )
        print("problem: ")
        print(
            f"\tnumber of vars = {self.model.nvars}"
        )
        print(
            f"\tnumber of nzeros = {self.model.nzeros}"
        )

        print(
            f"\tnumber of nodes = {self.comm.Get_size()}"

        )
        if isinstance(self.model, CardLogReg):
            print(
                f"\tnumber of sample points per node = {self.model.nsamples}"
            )
            print(
                f"\tnumber of total sample points = {self.model.nsamples * self.comm.Get_size()}"
            )

        print("solver settings:")

        print(
            f"\tM = {self.settings.big_m}"
        )
        if self.settings.sos:
            print(
                f"\tSOS-1: active"
            )
        else:
            print(
                f"\tSOS-1: inactive"
            )
        print(f"\tmain solver: {self.solver.__class__.__name__}")
        print(f"\tNLP solver = {RHADMM}")
        print(f"\tMIP solver = {GUROBI}")

        print(
            f"\tdistributed computing framework = MPI with mpi4py"
        )

    def _write_solution(self):
        write_solution(self.result, self.fname)

    def _print_solution(self):
        print(self.result)

    @staticmethod
    def clean_system():
        print("Path")

    def solve(self) -> DISCARTSolution:
        self.result = self.solver.solve()
        if self.comm.Get_rank() == ROOT_NODE:
            self._write_solution()
            self._print_solution()
        return self.result
