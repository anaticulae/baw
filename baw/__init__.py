###############################################################################
#                                Kiwi Project                                 #
#                                    2019                                     #
#                          Helmut Konrad Fahrendholz                          #
#                             kiwi@derspanier.de                              #
###############################################################################
from os.path import abspath
from os.path import dirname
from os.path import join

__version__ = '0.4.0'

THIS = dirname(__file__)
ROOT = abspath(join(THIS, '..'))  #  Path to installed baw-tool
