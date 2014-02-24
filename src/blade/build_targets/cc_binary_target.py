import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target
from cc_target_helper import CcTarget

class CcBinary(CcTarget):
    """A scons cc target subclass.

    This class is derived from SconsCCTarget and it generates the cc_binary
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
                 dynamic_link,
                 extra_cppflags,
                 extra_linkflags,
                 export_dynamic,
                 blade,
                 kwargs):
        """Init method.

        Init the cc target.

        """
        CcTarget.__init__(self,
                          name,
                          'cc_binary',
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
        self.data['dynamic_link'] = dynamic_link
        self.data['export_dynamic'] = export_dynamic

        cc_binary_config = configparse.blade_config.get_config('cc_binary_config')
        # add extra link library
        link_libs = var_to_list(cc_binary_config['extra_libs'])
        self._add_hardcode_library(link_libs)

    def _cc_binary(self):
        """_cc_binary rules. """
        env_name = self._env_name()
        var_name = self._generate_variable_name(self.path, self.name)

        platform = self.blade.get_scons_platform()
        if platform.get_gcc_version() > '4.5':
            link_flag_list = ['-static-libgcc', '-static-libstdc++']
            self._write_rule('%s.Append(LINKFLAGS=%s)' % (env_name, link_flag_list))

        (link_all_symbols_lib_list,
         lib_str,
         whole_link_flags) = self._get_static_deps_lib_list()
        if whole_link_flags:
            self._write_rule(
                    '%s.Append(LINKFLAGS=[%s])' % (env_name, whole_link_flags))

        if self.data.get('export_dynamic'):
            self._write_rule(
                '%s.Append(LINKFLAGS="-rdynamic")' % env_name)

        cc_config = configparse.blade_config.get_config('cc_config')
        linkflags = cc_config['linkflags']
        if linkflags:
            self._write_rule('%s.Append(LINKFLAGS=%s)' % (self._env_name(), linkflags))

        self._setup_extra_link_flags()

        self._write_rule('%s = %s.Program("%s", %s, %s)' % (
            var_name,
            env_name,
            self._target_file_path(),
            self._objs_name(),
            lib_str))
        self._write_rule('%s.Depends(%s, %s)' % (
            env_name,
            var_name,
            self._objs_name()))
        self._generate_target_explict_dependency(var_name)

        if link_all_symbols_lib_list:
            self._write_rule('%s.Depends(%s, [%s])' % (
                    env_name, var_name, ', '.join(link_all_symbols_lib_list)))

        self._write_rule('%s.Append(LINKFLAGS=str(version_obj[0]))' % env_name)
        self._write_rule('%s.Requires(%s, version_obj)' % (
                         env_name, var_name))

    def _dynamic_cc_binary(self):
        """_dynamic_cc_binary. """
        env_name = self._env_name()
        var_name = self._generate_variable_name(self.path, self.name)
        if self.data.get('export_dynamic'):
            self._write_rule('%s.Append(LINKFLAGS="-rdynamic")' % env_name)

        self._setup_extra_link_flags()

        lib_str = self._get_dynamic_deps_lib_list()
        self._write_rule('%s = %s.Program("%s", %s, %s)' % (
            var_name,
            env_name,
            self._target_file_path(),
            self._objs_name(),
            lib_str))
        self._write_rule('%s.Depends(%s, %s)' % (
            env_name,
            var_name,
            self._objs_name()))
        self._write_rule('%s.Append(LINKFLAGS=str(version_obj[0]))' % env_name)
        self._write_rule('%s.Requires(%s, version_obj)' % (
                         env_name, var_name))

        self._generate_target_explict_dependency(var_name)

    def scons_rules(self):
        """scons_rules.

        It outputs the scons rules according to user options.

        """
        self._prepare_to_generate_rule()

        self._cc_objects_rules()

        if self.data['dynamic_link']:
            self._dynamic_cc_binary()
        else:
            self._cc_binary()


def cc_binary(name,
              srcs=[],
              deps=[],
              warning='yes',
              defs=[],
              incs=[],
              export_incs=[],
              optimize=[],
              dynamic_link=False,
              extra_cppflags=[],
              extra_linkflags=[],
              export_dynamic=False,
              **kwargs):
    """cc_binary target. """
    cc_binary_target = CcBinary(name,
                                srcs,
                                deps,
                                warning,
                                defs,
                                incs,
                                export_incs,
                                optimize,
                                dynamic_link,
                                extra_cppflags,
                                extra_linkflags,
                                export_dynamic,
                                blade.blade,
                                kwargs)
    blade.blade.register_target(cc_binary_target)


build_rules.register_function(cc_binary)
