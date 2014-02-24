import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target
from cc_target_helper import CcTarget

class CcLibrary(CcTarget):
    """A cc target subclass.

    This class is derived from SconsTarget and it generates the library
    rules including dynamic library rules accoring to user option.

    """
    def __init__(self,
                 name,
                 srcs,
                 deps,
                 warning,
                 defs,
                 incs,
                 export_incs,
                 optimize,
                 always_optimize,
                 prebuilt,
                 link_all_symbols,
                 deprecated,
                 extra_cppflags,
                 extra_linkflags,
                 blade,
                 kwargs):
        """Init method.

        Init the cc target.

        """
        CcTarget.__init__(self,
                          name,
                          'cc_library',
                          srcs,
                          deps,
                          warning,
                          defs,
                          incs,
                          export_incs,
                          optimize,
                          extra_cppflags,
                          extra_linkflags,
                          blade,
                          kwargs)
        if prebuilt:
            self.type = 'prebuilt_cc_library'
            self.srcs = []
        self.data['link_all_symbols'] = link_all_symbols
        self.data['always_optimize'] = always_optimize
        self.data['deprecated'] = deprecated

    def scons_rules(self):
        """scons_rules.

        It outputs the scons rules according to user options.

        """
        self._prepare_to_generate_rule()

        options = self.blade.get_options()
        build_dynamic = (getattr(options, 'generate_dynamic', False) or
                         self.data.get('build_dynamic'))

        if self.type == 'prebuilt_cc_library':
            self._prebuilt_cc_library(build_dynamic)
        else:
            self._cc_objects_rules()
            self._cc_library()
            if build_dynamic:
                self._dynamic_cc_library()


def cc_library(name,
               srcs=[],
               deps=[],
               warning='yes',
               defs=[],
               incs=[],
               export_incs=[],
               optimize=[],
               always_optimize=False,
               pre_build=False,
               prebuilt=False,
               link_all_symbols=False,
               deprecated=False,
               extra_cppflags=[],
               extra_linkflags=[],
               **kwargs):
    """cc_library target. """
    target = CcLibrary(name,
                       srcs,
                       deps,
                       warning,
                       defs,
                       incs,
                       export_incs,
                       optimize,
                       always_optimize,
                       prebuilt or pre_build,
                       link_all_symbols,
                       deprecated,
                       extra_cppflags,
                       extra_linkflags,
                       blade.blade,
                       kwargs)
    if pre_build:
        console.warning("//%s:%s: 'pre_build' has been deprecated, "
                        "please use 'prebuilt'" % (target.path,
                                                   target.name))
    blade.blade.register_target(target)


build_rules.register_function(cc_library)
