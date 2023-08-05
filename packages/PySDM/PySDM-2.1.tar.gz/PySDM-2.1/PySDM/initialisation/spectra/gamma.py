"""
gamma spectrum implemented using
 [SciPy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html)
"""
from scipy.stats import gamma
from PySDM.initialisation.impl.spectrum import Spectrum

class Gamma(Spectrum):

    def __init__(self, norm_factor, k, theta):
        super().__init__(gamma, (
            k,       # shape factor
            0,       # loc
            theta    # scale
        ), norm_factor)
