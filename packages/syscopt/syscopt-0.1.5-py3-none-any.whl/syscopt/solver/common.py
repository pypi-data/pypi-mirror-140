from typing import List

from mpi4py import MPI
from mpi4py.MPI import Intercomm
from numpy import ndarray

from solver.DIS import *


def array_to_list(x: ndarray) -> List:
    out = []
    for item in x:
        out.append(float(item))
    return out


class MPIManager:
    def __init__(self, comm: Intercomm):
        self.comm = comm

    def get_rank(self) -> int:
        return self.comm.Get_rank()

    def get_size(self) -> int:
        return self.comm.Get_size()

    def all_reduce_vec(self, local_vec: ndarray, reduced_vec: ndarray, operation = MPI_SUM):
        op = MPI.SUM
        if operation is not MPI_SUM:
            pass
            # will be extended
        self.comm.Allreduce(
            [local_vec, MPI.DOUBLE],
            [reduced_vec, MPI.DOUBLE],
            op = op
        )

    def all_reduce(self, num: float, operation = MPI_SUM) -> float:
        op = MPI.SUM
        if operation is not MPI_SUM:
            pass
            # will be extended
        return self.comm.allreduce(num, op = op)

    def gather(self, num: float, root = ROOT_NODE):
        return self.comm.gather(num, root = root)

    def gather_vec(self, vec: ndarray, rcv_vec: ndarray, root = ROOT_NODE):

        self.comm.Gather([vec, MPI.DOUBLE], rcv_vec, root = root)

    def bcast_vec(self, vec: ndarray, from_node: int = 0):
        self.comm.Bcast([vec, MPI.DOUBLE], root = from_node)

    def bcast(self, num: float, from_node: int = 0):
        return self.comm.bcast(num, root = from_node)

    def all_gather(self, num: float) -> float:
        return self.comm.allgather(num)

    def all_gather_vec(self, vec: ndarray, rcv_vec: ndarray):
        self.comm.Allgather([vec, MPI.DOUBLE], [rcv_vec, MPI.DOUBLE])


def file_handler(fname: str, rank: int) -> str:
    pathlist = fname.split('/')

    filename = pathlist[-1]

    if POSTFIX not in fname:
        fname = PREFIX + str(rank) + "_" + filename + POSTFIX
    else:
        fname = PREFIX + str(rank) + "_" + filename
    pathlist[-1] = fname

    return "/".join(pathlist)
