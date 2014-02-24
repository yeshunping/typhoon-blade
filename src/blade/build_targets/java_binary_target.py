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


class JavaBinary(JavaTarget):
    """JavaLibrary"""
    def __init__(self, name, srcs, deps, **kwargs):
        type = 'java_binary'
        JavaTarget.__init__(self, name, type, srcs, deps, False, kwargs)


def java_binary(name,
                srcs=[],
                deps=[],
                **kwargs):
    """Define java_jar target. """
    target = JavaBinary(name,
                        srcs,
                        deps,
                        blade.blade,
                        kwargs)
    blade.blade.register_target(target)


build_rules.register_function(java_binary)