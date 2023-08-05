import json
import os.path
import pathlib
from abc import ABC, abstractmethod
from typing import Tuple

from numpy import array

from cli_handlers import get_current_time_stamp
from solver.DIS import POSTFIX, WORKING_DIR, OUTPUTS
from solver.common import array_to_list, file_handler
from solver.exeptions import ModelingError
from solver.model.domain import (
    CardQP,
    CardLogReg,
    DISCARTSettings,
    DIPOASettings,
    DISOASettings,
    ICard, DISCARTSolution
)


class IParser(ABC):
    @abstractmethod
    def __init__(self, fname: str):
        pass

    @abstractmethod
    def parse(self) -> ICard:
        pass


def parse_header(fname: str, rank: int) -> Tuple[str, str]:
    filepath = file_handler(fname, rank)
    with open(filepath, 'r') as input_data:
        data: dict = json.load(input_data)
    header = data['header']
    return header['date'], header['name']


def parse_cqp_input(fname: str, rank: int) -> CardQP:
    filepath = file_handler(fname, rank)
    with open(filepath, 'r') as input_data:
        qp_data: dict = json.load(input_data)
        qp_data = qp_data['problem']

    linear_term = qp_data.get("lin_term")
    quad_term = qp_data.get("quad_term")
    d = qp_data.get("const_term")
    nzeros = qp_data.get("nzeros")

    n = len(linear_term)
    c = array(linear_term).reshape(n, 1)
    q_list = []
    for row in quad_term:
        for key, value in row.items():
            q_list.append(value)
    Q = array(q_list)
    input_instance = CardQP(
        Q = Q,
        c = c,
        d = d,
        nzeros = nzeros
    )

    return input_instance


def parse_clogreg_input(fname: str, rank: int) -> CardLogReg:
    filepath = file_handler(fname, rank)
    with open(filepath, 'r') as input_data:
        log_reg_data: dict = json.load(input_data)
        log_reg_data = log_reg_data['problem']

    response = log_reg_data.get("response")
    samples = log_reg_data.get("samples")
    nzeros = log_reg_data.get("nzeros")
    m = len(samples)
    y = array(response).reshape(m, 1)
    x_list = []
    for row in samples:
        for key, value in row.items():
            x_list.append(value)
    X = array(x_list)
    input_instance = CardLogReg(
        X = X,
        y = y,
        nzeros = nzeros
    )
    return input_instance


def parse_settings(fname: str) -> DISCARTSettings:
    if POSTFIX not in fname:
        fname = fname + POSTFIX
    with open(fname, 'r') as input_settings:
        discart_settings_dict: dict = json.load(input_settings)

    dipoa_settings_dict: dict = discart_settings_dict['syscopt']['dipoa']
    disoa_settings_dict: dict = discart_settings_dict['syscopt']['disoa']
    discart_settings_dict = discart_settings_dict['syscopt']
    discart_setting = DISCARTSettings(
        verbose = discart_settings_dict.get('verbose'),
        sos = discart_settings_dict.get('sos'),
        algorithm = discart_settings_dict.get('algorithm'),
        disoa_opts = ...,
        dipoa_opts = ...,
        big_m = discart_settings_dict.get('bigm')
    )

    dipoa_settings: DIPOASettings = DIPOASettings(
        maxiter = dipoa_settings_dict.get("maxiter"),
        gap = dipoa_settings_dict.get("gap"),
        rgap = dipoa_settings_dict.get("rgap"),
        big_m = discart_setting.big_m,
        sos = discart_setting.sos,
        hybrid = False,
        verbose = dipoa_settings_dict.get("verbose"),
        soc = dipoa_settings_dict.get("soc")
    )
    disoa_settings: DISOASettings = DISOASettings(
        sos = discart_setting.sos,
        big_m = discart_setting.big_m,
        verbose = disoa_settings_dict.get('verbose')
    )

    discart_setting.dipoa_opts = dipoa_settings
    discart_setting.disoa_opts = disoa_settings
    return discart_setting


def write_solution(solution: DISCARTSolution, fname: str):
    if POSTFIX in fname:
        fname = fname.split('/')[-1].replace('.dis.json', "")
    else:
        fname = fname.split('/')[-1]
    root = WORKING_DIR
    file_name = f"results_{fname}_{get_current_time_stamp()}.dis.json"
    pathlib.Path(root + '/' + OUTPUTS).mkdir(exist_ok = True)
    file_path = os.path.join(root, OUTPUTS, file_name)

    solution_dict = {
        "syscopt - information": {
            "solver information": {
                "algorithm": solution.algorithm,
                "model": solution.model,
                "status": solution.status,
                "total time": solution.wct,
                "total NLP time": solution.total_nlp_time,
                "total MIP time": solution.total_mip_time,
            },
            "solution information": {
                "optimizer": array_to_list(solution.x),
                "objval": solution.objval,
                "number of linear cuts": solution.num_foc,
                "number of quadratic cuts": solution.num_soc,
                "number of lazy cuts": solution.num_lazy_constrs,
                "number of hybrid cuts": solution.num_hybrid_soc
            }
        }
    }

    with open(file_path, 'w') as output:
        json.dump(
            solution_dict,
            output,
            sort_keys = True,
            indent = 4,
            separators = (',', ': ')
        )


class HeaderParser(IParser):

    def __init__(self, fname: str, rank: int):
        self.fname = fname
        self.rank = rank

    def parse(self) -> Tuple[str, str]:
        try:
            return parse_header(self.fname, self.rank)
        except Exception as err:
            raise ModelingError(err)


class CQPInputParser(IParser):

    def __init__(self, fname: str, rank: int):
        self.fname = fname
        self.rank = rank

    def parse(self) -> CardQP:
        try:
            return parse_cqp_input(self.fname, self.rank)
        except FileNotFoundError as error:
            raise ModelingError(error)


class CLogRegInputParser(IParser):
    def __init__(self, fname: str, rank: int):
        self.fname = fname
        self.rank = rank

    def parse(self) -> CardLogReg:
        try:
            return parse_clogreg_input(self.fname, self.rank)
        except FileNotFoundError as error:
            raise ModelingError(error)


class SettingParser(IParser):
    def __init__(self, fname: str):
        self.fname = fname

    def parse(self) -> DISCARTSettings:
        try:
            return parse_settings(self.fname)
        except FileNotFoundError as error:
            raise ModelingError(error)
