import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target
from cc_binary_target import cc_binary

def cc_benchmark(name, deps=[], **kwargs):
    """cc_benchmark target. """
    cc_config = configparse.blade_config.get_config('cc_config')
    benchmark_libs = cc_config['benchmark_libs']
    benchmark_main_libs = cc_config['benchmark_main_libs']
    deps = var_to_list(deps) + benchmark_libs + benchmark_main_libs
    cc_binary(name=name, deps=deps, **kwargs)


build_rules.register_function(cc_benchmark)
