# Copyright (c) 2013 Tencent Inc.
# All rights reserved.
#
# Author: CHEN Feng <phongchen@tencent.com>
# Created: Jun 26, 2013


"""
Implement java_library, java_binary and java_test
"""


import os
import blade

import build_rules

from blade_util import var_to_list
from target import Target
from java_target_helper import JavaTarget


class JavaLibrary(JavaTarget):
    """JavaLibrary"""
    def __init__(self, name, srcs, deps, prebuilt, **kwargs):
        type = 'java_library'
        if prebuilt:
            type = 'prebuilt_java_library'
        JavaTarget.__init__(self, name, type, srcs, deps, prebuilt, kwargs)


def java_library(name,
                 srcs=[],
                 deps=[],
                 prebuilt=False,
                 **kwargs):
    """Define java_jar target. """
    target = JavaLibrary(name,
                         srcs,
                         deps,
                         prebuilt,
                         blade.blade,
                         kwargs)
    blade.blade.register_target(target)


build_rules.register_function(java_library)
