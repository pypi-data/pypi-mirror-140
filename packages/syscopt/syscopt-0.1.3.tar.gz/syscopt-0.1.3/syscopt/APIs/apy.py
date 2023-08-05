import json
import os.path
import pathlib
from abc import ABC, abstractmethod
from typing import Tuple, List

from numpy import ndarray, diagflat
from numpy.linalg import eig
from numpy.random import rand

from syscopt.solver.DIS import WORKING_DIR, INPUTS, BINS
from syscopt.cli_handlers import get_current_time_stamp
from syscopt.solver.DIS import PREFIX, POSTFIX


class ModelMixin:
    @staticmethod
    def get_date():
        return get_current_time_stamp()


class IProblem(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def to_json(self, rank: int):
        pass

    @abstractmethod
    def _create_model(self):
        pass

    @abstractmethod
    def _write_to_file(self, rank: int):
        pass


class CQP(IProblem, ModelMixin):

    def __init__(self, Q: ndarray, q: ndarray, d: float, nzeros: int, name: str, rank: int):
        self.Q = Q
        self.q = q
        self.d = d
        self.nzeros = nzeros
        self.date = self.get_date()
        self.name = name + "_" + "qp"
        self.header = {}
        self.problem = {}
        self.json_dict = {}
        self.json_str = ""
        self.to_json(rank)

    def _create_model(self):
        self.header['date'] = self.date
        self.header['name'] = self.name

        self.problem['lin_term'] = [float(item) for item in self.q]
        self.problem['quad_term'] = []
        for i in range(self.Q.shape[0]):
            row = {
                f"row_{i}": [float(item) for item in self.Q[i, :]]
            }
            self.problem['quad_term'].append(row)
        self.problem['const_term'] = self.d
        self.problem['nzeros'] = self.nzeros
        self.json_dict['header'] = self.header
        self.json_dict['problem'] = self.problem

    def _write_to_file(self, rank: int):
        root = WORKING_DIR
        filename = PREFIX + str(rank) + "_" + self.name + POSTFIX
        pathlib.Path(root + '/' + INPUTS).mkdir(exist_ok = True)
        target = os.path.join(root, INPUTS, filename)
        with open(target, 'w') as jsonwriter:
            jsonwriter.write(self.json_str)

    def to_json(self, rank: int):
        self._create_model()
        self.json_str = json.dumps(self.json_dict, sort_keys = True,
                                   indent = 4,
                                   separators = (',', ': '))
        self._write_to_file(rank)


class CLogReg(IProblem, ModelMixin):
    def __init__(self, X: ndarray, y: ndarray, nzeros: int, name: str, rank: int):
        self.X = X
        self.y = y
        self.nzeros = nzeros
        self.date = self.get_date()
        self.name = name + "_" + "logreg"
        self.header = {}
        self.problem = {}
        self.json_dict = {}
        self.json_str = ""
        self.to_json(rank)

    def _create_model(self):
        self.header['date'] = self.date
        self.header['name'] = self.name

        self.problem['response'] = [float(item) for item in self.y]
        self.problem['samples'] = []
        for i in range(self.X.shape[0]):
            row = {
                f"row_{i}": [float(item) for item in self.X[i, :]]
            }
            self.problem['samples'].append(row)
        self.problem['nzeros'] = self.nzeros
        self.json_dict['header'] = self.header
        self.json_dict['problem'] = self.problem

    def _write_to_file(self, rank: int):
        root = WORKING_DIR
        filename = PREFIX + str(rank) + "_" + self.name + POSTFIX
        pathlib.Path(root + '/' + INPUTS).mkdir(exist_ok = True)
        target = os.path.join(root, INPUTS, filename)
        with open(target, 'w') as jsonwriter:
            jsonwriter.write(self.json_str)

    def to_json(self, rank: int):
        self._create_model()
        self.json_str = json.dumps(self.json_dict, sort_keys = True,
                                   indent = 4,
                                   separators = (',', ': '))
        self._write_to_file(rank)


class CLinearRegression(CQP):
    def __init__(self, X: ndarray, y: ndarray, nzeros: int, name: str, rank: int):
        self.X = X
        self.y = y
        Q = self.X.T @ self.X
        q = - 2 * self.X.T @ y
        d = float(self.y.T @ self.y)
        super().__init__(Q, q, d, nzeros, name, rank)


def create_mpi_run(models: List[IProblem], file_name: str):
    size = len(models)
    model = models[0]
    root = WORKING_DIR
    if isinstance(model, CQP) or isinstance(model, CLinearRegression):
        target = os.path.join(root, f"{INPUTS}/{file_name}_qp.dis.json")
    elif isinstance(model, CLogReg):
        target = os.path.join(root, f"{INPUTS}/{file_name}_logreg.dis.json")
    else:
        raise ValueError("Model is not valid")
    ROOT_MPI = os.path.dirname(os.path.dirname(__file__))
    arg = ['mpiexec', "-n", str(size), f"{ROOT_MPI}/syscopt-cli", "run", target]
    command = " ".join(arg)
    msg = f"echo Executing MPI program {model.name}\n" \
          f"echo command: {command}\n"
    pathlib.Path(os.path.join(root, BINS)).mkdir(exist_ok = True)
    bin_filename = "mpi_exec_" + file_name
    target_file = os.path.join(root, f"{BINS}/{bin_filename}")
    with open(target_file, 'w+') as writer:
        writer.write(msg)
        writer.write(command)

    print(f"{bin_filename} has been created in {target_file.split(bin_filename)[0]}. please run 'sh {target_file}'")


def create_convex_qp(n: int) -> Tuple[ndarray, ndarray, float]:
    Q = rand(n, n) + 3
    Q = Q.T + Q

    w, v = eig(Q)

    Q = v @ diagflat(1 + rand(n, 1)) @ v.T

    q = rand(n, 1)

    d = float(rand(1, 1))

    return Q, q, d


def create_random_log_reg(m: int, n: int) -> Tuple[ndarray, ndarray]:
    X = rand(m, n)
    y = rand(m, 1)
    y[y <= 0.5] = 0.0
    y[y > 0.5] = 1.0
    return X, y


def create_random_lin_reg(m: int, n: int) -> Tuple[ndarray, ndarray]:
    X = rand(m, n)
    y = rand(m, 1)
    return X, y
