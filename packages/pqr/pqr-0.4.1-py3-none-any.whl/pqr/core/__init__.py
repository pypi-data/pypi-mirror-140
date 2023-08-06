"""Package with core functionality for backtesting portfolios and creating
benchmarks. Provides tools to build portfolios, allocate positions, calculate
returns and various ways to build a benchmark.

The process of backtesting can be split into 3 steps:
    * Picking
    * Allocation (weighting)
    * Calculating returns

This package provides necessary functionality for all of these steps, but
specific picking strategies are not presented here.
"""

from pqr.core.allocation import *
from pqr.core.benchmark import *
from pqr.core.portfolio import *
from pqr.core.returns import *
