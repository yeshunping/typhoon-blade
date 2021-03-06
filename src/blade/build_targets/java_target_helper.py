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


class JavaTarget(Target):
    """A java jar target subclass.

    This class is derived from Target and generates relates java jar
    rules.

    """
    def __init__(self,
                 name,
                 type,
                 srcs,
                 deps,
                 prebuilt,
                 blade,
                 kwargs):
        """Init method.

        Init the java jar target.

        """
        srcs = var_to_list(srcs)
        deps = var_to_list(deps)

        Target.__init__(self,
                        name,
                        type,
                        srcs,
                        deps,
                        blade,
                        kwargs)

    def _java_jar_gen_class_root(self, path, name):
        """Gen class root. """
        return os.path.join(self.build_path, path, '%s.classes' % name)

    def _dep_is_jar_to_compile(self, dep):
        """Check the target is java_jar target or not. """
        targets = self.blade.get_build_targets()
        target_type = targets[dep].type
        return ('java_jar' in target_type and 'prebuilt' not in target_type)

    def _java_jar_deps_list(self, deps):
        """Returns a jar list string that this targets depends on. """
        jar_list = []
        for jar in deps:
            if not jar:
                continue

            if not self._dep_is_jar_to_compile(jar):
                continue

            jar_name = '%s.jar' % jar[1]
            jar_path = os.path.join(self.build_path, jar[0], jar_name)
            jar_list.append(jar_path)
        return jar_list

    def scons_rules(self):
        """scons_rules.
        Description
        -----------
        It outputs the scons rules according to user options.

        """
        self._generate_classes()
        self._generate_jar()
