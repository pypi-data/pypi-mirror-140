# (c) 2021 Dr. Flavio ABREU ARAUJO

from ._version import __version__
__author__ = 'Flavio ABREU ARAUJO'
__email__ = 'flavio.abreuaraujo@uclouvain.be'

try:
    from .binaries import OVF_File_py
    from .helper_funcs import *
    from .ovf_handler import *
except ImportError:
    raise ImportError('PyOVF not compiled for your python version.')
