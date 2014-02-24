# Copyright (c) 2011 Tencent Inc.
# All rights reserved.
#
# Author: Michaelpeng <michaelpeng@tencent.com>
# Date:   October 20, 2011


"""
 This is the cc_target module which is the super class
 of all of the scons cc targets, like cc_library, cc_binary.

"""


import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target


class CcTarget(Target):
    """A scons cc target subclass.

    This class is derived from SconsTarget and it is the base class
    of cc_library, cc_binary etc.

    """
    def __init__(self,
                 name,
                 target_type,
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
                 kwargs):
        """Init method.

        Init the cc target.

        """
        srcs = var_to_list(srcs)
        deps = var_to_list(deps)
        defs = var_to_list(defs)
        incs = var_to_list(incs)
        export_incs = var_to_list(export_incs)
        opt = var_to_list(optimize)
        extra_cppflags = var_to_list(extra_cppflags)
        extra_linkflags = var_to_list(extra_linkflags)

        Target.__init__(self,
                        name,
                        target_type,
                        srcs,
                        deps,
                        blade,
                        kwargs)

        self.data['warning'] = warning
        self.data['defs'] = defs
        self.data['incs'] = incs
        self.data['export_incs'] = export_incs
        self.data['optimize'] = opt
        self.data['extra_cppflags'] = extra_cppflags
        self.data['extra_linkflags'] = extra_linkflags

        self._check_defs()
        self._check_incorrect_no_warning()

    def _check_deprecated_deps(self):
        """check that whether it depends upon a deprecated library. """
        for dep in self.deps:
            target = self.target_database.get(dep, {})
            if target.data.get('deprecated'):
                replaced_targets = target.deps
                replaced_target = ''
                if replaced_targets:
                    replaced_target = replaced_targets[0]
                console.warning('//%s:%s : '
                                '//%s:%s has been deprecated, '
                                'please depends on //%s:%s' % (
                                    self.path, self.name,
                                    target.path, target.name,
                                    replaced_target[0], replaced_target[1]))

    def _prepare_to_generate_rule(self):
        """Should be overridden. """
        self._check_deprecated_deps()
        self._clone_env()

    def _clone_env(self):
        """Select env. """
        env_name = self._env_name()
        warning = self.data.get('warning', '')
        if warning == 'yes':
            self._write_rule('%s = env_with_error.Clone()' % env_name)
        else:
            self._write_rule('%s = env_no_warning.Clone()' % env_name)

    __cxx_keyword_list = frozenset([
        'and', 'and_eq', 'alignas', 'alignof', 'asm', 'auto',
        'bitand', 'bitor', 'bool', 'break', 'case', 'catch',
        'char', 'char16_t', 'char32_t', 'class', 'compl', 'const',
        'constexpr', 'const_cast', 'continue', 'decltype', 'default',
        'delete', 'double', 'dynamic_cast', 'else', 'enum',
        'explicit', 'export', 'extern', 'false', 'float', 'for',
        'friend', 'goto', 'if', 'inline', 'int', 'long', 'mutable',
        'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr',
        'operator', 'or', 'or_eq', 'private', 'protected', 'public',
        'register', 'reinterpret_cast', 'return', 'short', 'signed',
        'sizeof', 'static', 'static_assert', 'static_cast', 'struct',
        'switch', 'template', 'this', 'thread_local', 'throw',
        'true', 'try', 'typedef', 'typeid', 'typename', 'union',
        'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t',
        'while', 'xor', 'xor_eq'])

    def _check_defs(self):
        """_check_defs.

        It will warn if user defines cpp keyword in defs list.

        """
        defs_list = self.data.get('defs', [])
        for macro in defs_list:
            pos = macro.find('=')
            if pos != -1:
                macro = macro[0:pos]
            if macro in CcTarget.__cxx_keyword_list:
                console.warning('DO NOT define c++ keyword %s as macro' % macro)

    def _check_incorrect_no_warning(self):
        """check if warning=no is correctly used or not. """
        warning = self.data.get('warning', 'yes')
        srcs = self.srcs
        if not srcs or warning != 'no':
            return

        keywords_list = self.blade.get_sources_keyword_list()
        for keyword in keywords_list:
            if keyword in self.path:
                return

        illegal_path_list = []
        for keyword in keywords_list:
            illegal_path_list += [s for s in srcs if not keyword in s]

        if illegal_path_list:
            console.warning("//%s:%s : warning='no' is only allowed "
                            "for code in thirdparty." % (
                                self.key[0], self.key[1]))

    def _objs_name(self):
        """_objs_name.

        Concatinating target path, target name to be objs var and returns.

        """
        return 'objs_%s' % self._generate_variable_name(self.path,
                                                        self.name)

    def _prebuilt_cc_library_build_path(self, path='', name='', dynamic=0):
        """Returns the build path of the prebuilt cc library. """
        if not path:
            path = self.path
        if not name:
            name = self.name
        suffix = 'a'
        if dynamic:
            suffix = 'so'
        return os.path.join(self.build_path, path, 'lib%s.%s' % (name, suffix))

    def _prebuilt_cc_library_src_path(self, path='', name='', dynamic=0):
        """Returns the source path of the prebuilt cc library. """
        if not path:
            path = self.path
        if not name:
            name = self.name
        options = self.blade.get_options()
        suffix = 'a'
        if dynamic:
            suffix = 'so'
        return os.path.join(path, 'lib%s_%s' % (options.m, options.profile),
                            'lib%s.%s' % (name, suffix))

    def _setup_cc_flags(self):
        """_setup_cc_flags. """
        env_name = self._env_name()
        flags_from_option, incs_list = self._get_cc_flags()
        if flags_from_option:
            self._write_rule('%s.Append(CPPFLAGS=%s)' % (env_name, flags_from_option))
        if incs_list:
            self._write_rule('%s.Append(CPPPATH=%s)' % (env_name, incs_list))

    def _setup_as_flags(self):
        """_setup_as_flags. """
        env_name = self._env_name()
        as_flags = self._get_as_flags()
        if as_flags:
            self._write_rule('%s.Append(ASFLAGS=%s)' % (env_name, as_flags))

    def _setup_extra_link_flags(self):
        """extra_linkflags. """
        extra_linkflags = self.data.get('extra_linkflags')
        if extra_linkflags:
            self._write_rule('%s.Append(LINKFLAGS=%s)' % (self._env_name(), extra_linkflags))

    def _check_gcc_flag(self, gcc_flag_list):
        options = self.blade.get_options()
        gcc_flags_list_checked = []
        for flag in gcc_flag_list:
            if flag == '-fno-omit-frame-pointer':
                if options.profile != 'release':
                    continue
            gcc_flags_list_checked.append(flag)
        return gcc_flags_list_checked

    def _get_optimize_flags(self):
        """get optimize flags such as -O2"""
        oflags = []
        opt_list = self.data.get('optimize')
        if not opt_list:
            cc_config = configparse.blade_config.get_config('cc_config')
            opt_list = cc_config['optimize']
        if opt_list:
            for flag in opt_list:
                if flag.startswith('-'):
                    oflags.append(flag)
                else:
                    oflags.append('-' + flag)
        else:
            oflags = ['-O2']
        return oflags

    def _get_cc_flags(self):
        """_get_cc_flags.

        Return the cpp flags according to the BUILD file and other configs.

        """
        cpp_flags = []

        # Warnings
        if self.data.get('warning', '') == 'no':
            cpp_flags.append('-w')

        # Defs
        defs = self.data.get('defs', [])
        cpp_flags += [('-D' + macro) for macro in defs]

        # Optimize flags

        if (self.blade.get_options().profile == 'release' or
            self.data.get('always_optimize')):
            cpp_flags += self._get_optimize_flags()

        # Add the compliation flags here
        # 1. -fno-omit-frame-pointer to release
        blade_gcc_flags = ['-fno-omit-frame-pointer']
        blade_gcc_flags_checked = self._check_gcc_flag(blade_gcc_flags)
        cpp_flags += list(set(blade_gcc_flags_checked).difference(set(cpp_flags)))

        cpp_flags += self.data.get('extra_cppflags', [])

        # Incs
        incs = self.data.get('incs', [])
        if not incs:
            incs = self.data.get('export_incs', [])
        new_incs_list = [os.path.join(self.path, inc) for inc in incs]
        new_incs_list += self._export_incs_list()
        # Remove duplicate items in incs list and keep the order
        incs_list = []
        for inc in new_incs_list:
            new_inc = os.path.normpath(inc)
            if new_inc not in incs_list:
                incs_list.append(new_inc)

        return (cpp_flags, incs_list)

    def _get_as_flags(self):
        """_get_as_flags.

        Return the as flags according to the build architecture.

        """
        options = self.blade.get_options()
        as_flags = ["--" + options.m]
        return as_flags


    def _dep_is_library(self, dep):
        """_dep_is_library.

        Returns
        -----------
        True or False: Whether this dep target is library or not.

        Description
        -----------
        Whether this dep target is library or not.

        """
        build_targets = self.blade.get_build_targets()
        target_type = build_targets[dep].type
        return ('library' in target_type or 'plugin' in target_type)

    def _export_incs_list(self):
        """_export_incs_list.
        TODO
        """
        deps = self.expanded_deps
        inc_list = []
        for lib in deps:
            # lib is (path, libname) pair.
            if not lib:
                continue

            if not self._dep_is_library(lib):
                continue

            # system lib
            if lib[0] == '#':
                continue

            target = self.target_database[lib]
            for inc in target.data.get('export_incs', []):
                path = os.path.normpath('%s/%s' % (lib[0], inc))
                inc_list.append(path)

        return inc_list

    def _static_deps_list(self):
        """_static_deps_list.

        Returns
        -----------
        link_all_symbols_lib_list: the libs to link all its symbols into target
        lib_list: the libs list to be statically linked into static library

        Description
        -----------
        It will find the libs needed to be linked into the target statically.

        """
        build_targets = self.blade.get_build_targets()
        deps = self.expanded_deps
        lib_list = []
        link_all_symbols_lib_list = []
        for dep in deps:
            if not self._dep_is_library(dep):
                continue

            # system lib
            if dep[0] == '#':
                lib_name = "'%s'" % dep[1]
            else:
                lib_name = self._generate_variable_name(dep[0], dep[1])

            if build_targets[dep].data.get('link_all_symbols'):
                link_all_symbols_lib_list.append(lib_name)
            else:
                lib_list.append(lib_name)

        return (link_all_symbols_lib_list, lib_list)

    def _dynamic_deps_list(self):
        """_dynamic_deps_list.

        Returns
        -----------
        lib_list: the libs list to be dynamically linked into dynamic library

        Description
        -----------
        It will find the libs needed to be linked into the target dynamically.

        """
        build_targets = self.blade.get_build_targets()
        deps = self.expanded_deps
        lib_list = []
        for lib in deps:
            if not self._dep_is_library(lib):
                continue

            if (build_targets[lib].type == 'cc_library' and
                not build_targets[lib].srcs):
                continue
            # system lib
            if lib[0] == '#':
                lib_name = "'%s'" % lib[1]
            else:
                lib_name = self._generate_variable_name(lib[0],
                                                        lib[1],
                                                        'dynamic')

            lib_list.append(lib_name)

        return lib_list

    def _get_static_deps_lib_list(self):
        """Returns a tuple that needed to write static deps rules. """
        (link_all_symbols_lib_list, lib_list) = self._static_deps_list()
        lib_str = 'LIBS=[%s]' % ','.join(lib_list)
        whole_link_flags = []
        if link_all_symbols_lib_list:
            whole_link_flags = ['"-Wl,--whole-archive"']
            for i in link_all_symbols_lib_list:
                whole_link_flags.append(i)
            whole_link_flags.append('"-Wl,--no-whole-archive"')
        return (link_all_symbols_lib_list, lib_str, ', '.join(whole_link_flags))

    def _get_dynamic_deps_lib_list(self):
        """Returns the libs string. """
        lib_list = self._dynamic_deps_list()
        lib_str = 'LIBS=[]'
        if lib_list:
            lib_str = 'LIBS=[%s]' % ','.join(lib_list)
        return lib_str

    def _prebuilt_cc_library(self, dynamic=0):
        """prebuilt cc library rules. """
        build_targets = self.blade.get_build_targets()
        prebuilt_target_file = ''
        prebuilt_src_file = ''
        prebuilt_symlink = ''
        allow_only_dynamic = True
        need_static_lib_targets = ['cc_test',
                                   'cc_binary',
                                   'cc_benchmark',
                                   'cc_plugin',
                                   'swig_library']
        for key in build_targets:
            if (self.key in build_targets[key].expanded_deps and
                build_targets[key].type in need_static_lib_targets):
                allow_only_dynamic = False

        var_name = self._generate_variable_name(self.path,
                                                self.name)
        if not allow_only_dynamic:
            self._write_rule(
                    'Command("%s", "%s", Copy("$TARGET", "$SOURCE"))' % (
                             self._prebuilt_cc_library_build_path(),
                             self._prebuilt_cc_library_src_path()))
            self._write_rule('%s = top_env.File("%s")' % (
                             var_name,
                             self._prebuilt_cc_library_build_path()))
        if dynamic:
            prebuilt_target_file = self._prebuilt_cc_library_build_path(
                                            self.path,
                                            self.name,
                                            dynamic=1)
            prebuilt_src_file = self._prebuilt_cc_library_src_path(
                                            self.path,
                                            self.name,
                                            dynamic=1)
            self._write_rule(
                    'Command("%s", "%s", Copy("$TARGET", "$SOURCE"))' % (
                     prebuilt_target_file,
                     prebuilt_src_file))
            var_name = self._generate_variable_name(self.path,
                                                    self.name,
                                                    'dynamic')
            self._write_rule('%s = top_env.File("%s")' % (
                        var_name,
                        prebuilt_target_file))
            prebuilt_symlink = os.path.realpath(prebuilt_src_file)
            prebuilt_symlink = os.path.basename(prebuilt_symlink)
            self.file_and_link = (prebuilt_target_file, prebuilt_symlink)
        else:
            self.file_and_link = None

    def _cc_library(self):
        """_cc_library.

        It will output the cc_library rule into the buffer.

        """
        var_name = self._generate_variable_name(self.path, self.name)
        self._write_rule('%s = %s.Library("%s", %s)' % (
                var_name,
                self._env_name(),
                self._target_file_path(),
                self._objs_name()))
        self._write_rule('%s.Depends(%s, %s)' % (
                self._env_name(),
                var_name,
                self._objs_name()))
        self._generate_target_explict_dependency(var_name)

    def _dynamic_cc_library(self):
        """_dynamic_cc_library.

        It will output the dynamic_cc_library rule into the buffer.

        """
        self._setup_extra_link_flags()

        var_name = self._generate_variable_name(self.path,
                                                self.name,
                                                'dynamic')

        lib_str = self._get_dynamic_deps_lib_list()
        if self.srcs or self.expanded_deps:
            self._write_rule('%s.Append(LINKFLAGS=["-Xlinker", "--no-undefined"])'
                             % self._env_name())
            self._write_rule('%s = %s.SharedLibrary("%s", %s, %s)' % (
                    var_name,
                    self._env_name(),
                    self._target_file_path(),
                    self._objs_name(),
                    lib_str))
            self._write_rule('%s.Depends(%s, %s)' % (
                    self._env_name(),
                    var_name,
                    self._objs_name()))
        self._generate_target_explict_dependency(var_name)

    def _cc_objects_rules(self):
        """_cc_objects_rules.

        Generate the cc objects rules for the srcs in srcs list.

        """
        target_types = ['cc_library',
                        'cc_binary',
                        'cc_test',
                        'cc_plugin']

        if not self.type in target_types:
            console.error_exit('logic error, type %s err in object rule' % self.type)

        path = self.path
        objs_name = self._objs_name()
        env_name = self._env_name()

        self._setup_cc_flags()
        self._setup_as_flags()

        objs = []
        sources = []
        for src in self.srcs:
            obj = '%s_%s_object' % (self._generate_variable_name(path, src),
                                    self._regular_variable_name(self.name))
            target_path = os.path.join(
                    self.build_path, path, '%s.objs' % self.name, src)
            self._write_rule(
                    '%s = %s.SharedObject(target = "%s" + top_env["OBJSUFFIX"]'
                    ', source = "%s")' % (obj,
                                          env_name,
                                          target_path,
                                          self._target_file_path(path, src)))
            self._write_rule('%s.Depends(%s, "%s")' % (
                             env_name,
                             obj,
                             self._target_file_path(path, src)))
            sources.append(self._target_file_path(path, src))
            objs.append(obj)
        self._write_rule('%s = [%s]' % (objs_name, ','.join(objs)))
        return sources

