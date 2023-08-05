## SYStem of Cardinality OPtimization (SYSCOPT)

**SysCopt** is a Python framework designed to solve
_Distributed Cardinality Constrained Optimization (DCCO)_ problems
over peer-to-peer networks of computing nodes.

Syscopt consists of three distributed algorithms to solve DCCO problems whereby an iteration procedure is applied by
each node of the network which alternates communication and computation phases until a solution is found.

SysCopt provides the following distributed algorithms:
- Distributed Primal Outer Approximation (DiPOA)
  - DiPOA implements distributed OA algorithm, and it features second order outer
  approximations, event triggered cut generation, specialized feasibility pump, etc.
- Distributed Single-Tree Outer Approximation (DiSOA)
  - DiSOA implements distributed LP/NLP based Branch and Bound method
- Distributed Hybrid Outer Approximation (DIHOA).
  - DIHOA is a meta and event-driven algorithm that combines 
    DIPOA and DISOA  in such a way that both algorithms 
    collaborate on providing the solution for the problem
    
### Main Dependencies
1. Scipy
2. Numpy
3. Gurobipy 9.1.2
4. Gurobi Optimization Solver
5. Mpi4py

Please see requirements.txt file to see full list of dependencies.

### Install
```commandline
pip install syscopt
```