# <include absolute path to a python >= 3.8 env with requests installed>

from src import utils

utils.execute(auto_tag=utils.parse_autotag_flag())
