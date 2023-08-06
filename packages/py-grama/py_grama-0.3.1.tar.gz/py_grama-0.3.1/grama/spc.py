# Statistical Process Control tools
__all__ = []

from scipy.special import gamma
from grama import make_symbolic
from numpy import sqrt

def c_sd(n):
    r"""Anti-biasing constant for aggregate standard deviation

    References:
        Kenett and Zacks, Modern Industrial Statistics (2014) 2nd Ed
    """
    return gamma(n/2) / gamma( (n-1)/2 ) * sqrt( 2 / (n-1) )
