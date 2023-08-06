__version__= "0.0.1"
__doc__ = "GemAct is a comprehensive actuarial package, based on the collective risk theory framework, that offers a comprehensive set of tools for non-life (re)insurance pricing, stochastic claims reserving, and risk aggregation.\nThe variety of available functionalities makes GemAct modeling very flexible and provides actuarial scientists and practitioners with a powerful tool that fits into the expanding community of Python programming language."

from twiggy import quick_setup,log
import gemact.gemdata as gemdata
from gemact.lossmodule import *
from gemact.lossreserve import *
from gemact.lossaggregation import *
from gemact.distributions import *

quick_setup()
logger= log.name('GemAct')

