import os

WORKING_DIR = os.getcwd()
INPUTS = 'inputs'
OUTPUTS = 'outputs'
LOGS = 'logs'
BINS = "bins"
OPTIMAL = 0
INFEASIBLE = 1
ROOT = 0
AD_MU = 10
AD_T = 5
MAX_ITER_REACHED = 1
ROOT_NODE = 0
DISCART_INF = 1e10
EVENT_GAP = 1e-3
INITIAL_ITER = 3
DIPOA_UB = 1e9
DIPOA_LB = - DIPOA_UB
MPI_SUM = "sum"
GITHUB = "github.com/alirezalm"
EMAIL = "alireza.lm69@gmail.com"
RHADMM = "relaxed hybrid admm"
GUROBI = "gurobi"
HYBRID_GAP = 1e-2
POSTFIX = ".dis.json"
PREFIX = "node_"
ITER_COUNT = 10