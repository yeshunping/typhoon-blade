import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target
from cc_target_helper import CcTarget

class CcPlugin(CcTarget):
    """A scons cc target subclass.

    This class is derived from SconsCCTarget and it generates the cc_plugin
    rules according to user options.

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
                 prebuilt,
                 extra_cppflags,
                 extra_linkflags,
                 blade,
                 kwargs):
        """Init method.

        Init the cc plugin target.

        """
        CcTarget.__init__(self,
                          name,
                          'cc_plugin',
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

    def scons_rules(self):
        """scons_rules.

        It outputs the scons rules according to user options.

        """
        self._prepare_to_generate_rule()

        env_name = self._env_name()
        var_name = self._generate_variable_name(self.path,
                                                self.name,
                                                'dynamic')

        self._cc_objects_rules()
        self._setup_extra_link_flags()

        (link_all_symbols_lib_list,
         lib_str,
         whole_link_flags) = self._get_static_deps_lib_list()
        if whole_link_flags:
            self._write_rule(
                    '%s.Append(LINKFLAGS=[%s])' % (env_name, whole_link_flags))

        if self.srcs or self.expanded_deps:
            self._write_rule('%s = %s.SharedLibrary("%s", %s, %s)' % (
                    var_name,
                    env_name,
                    self._target_file_path(),
                    self._objs_name(),
                    lib_str))

        if link_all_symbols_lib_list:
            self._write_rule('%s.Depends(%s, [%s])' % (
                env_name, var_name, ', '.join(link_all_symbols_lib_list)))

        self._generate_target_explict_dependency(var_name)


def cc_plugin(name,
              srcs=[],
              deps=[],
              warning='yes',
              defs=[],
              incs=[],
              export_incs=[],
              optimize=[],
              prebuilt=False,
              pre_build=False,
              extra_cppflags=[],
              extra_linkflags=[],
              **kwargs):
    """cc_plugin target. """
    target = CcPlugin(name,
                      srcs,
                      deps,
                      warning,
                      defs,
                      incs,
                      export_incs,
                      optimize,
                      prebuilt or pre_build,
                      extra_cppflags,
                      extra_linkflags,
                      blade.blade,
                      kwargs)
    if pre_build:
        console.warning("//%s:%s: 'pre_build' has been deprecated, "
                        "please use 'prebuilt'" % (target.path,
                                                   target.name))
    blade.blade.register_target(target)


build_rules.register_function(cc_plugin)

