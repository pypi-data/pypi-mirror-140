from setuptools import setup, find_packages

import metadata

setup(
    name = "syscopt",
    version = metadata.__version__,
    description = "a Python framework designed to solve Distributed Cardinality Constrained Optimization",
    url = "https://github.com/Alirezalm/syscopt",
    author = metadata.__author__,
    author_email = metadata.__authoremail__,
    packages = find_packages(include = ["syscopt*", ".json*"]),
    package_data={'': ['syscopt-cli']},
    include_package_data = True,
    install_requires = [
        "click",
        "fonttools",
        "gurobipy==9.1.2",
        "mpi4py",
        "numpy",
        "scipy",
    ],

)
