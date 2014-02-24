import os
import blade
import configparse

import console
import build_rules
from blade_util import var_to_list
from target import Target
from cc_binary_target import CcBinary

# See http://google-perftools.googlecode.com/svn/trunk/doc/heap_checker.html
HEAP_CHECK_VALUES = set([
    'minimal',
    'normal',
    'strict',
    'draconian',
    'as-is',
    'local',
])


class CcTest(CcBinary):
    """A scons cc target subclass.

    This class is derived from SconsCCTarget and it generates the cc_test
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
                 testdata,
                 extra_cppflags,
                 extra_linkflags,
                 export_dynamic,
                 always_run,
                 exclusive,
                 heap_check,
                 heap_check_debug,
                 blade,
                 kwargs):
        """Init method.

        Init the cc target.

        """
        cc_test_config = configparse.blade_config.get_config('cc_test_config')
        if dynamic_link is None:
            dynamic_link = cc_test_config['dynamic_link']

        CcBinary.__init__(self,
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
                          kwargs)
        self.type = 'cc_test'
        self.data['testdata'] = var_to_list(testdata)
        self.data['always_run'] = always_run
        self.data['exclusive'] = exclusive

        gtest_lib = var_to_list(cc_test_config['gtest_libs'])
        gtest_main_lib = var_to_list(cc_test_config['gtest_main_libs'])

        # Hardcode deps rule to thirdparty gtest main lib.
        self._add_hardcode_library(gtest_lib)
        self._add_hardcode_library(gtest_main_lib)

        if heap_check is None:
            heap_check = cc_test_config.get('heap_check', '')
        else:
            if heap_check not in HEAP_CHECK_VALUES:
                console.error_exit('//%s:%s: heap_check can only be in %s' % (
                    self.path, self.name, HEAP_CHECK_VALUES))

        perftools_lib = var_to_list(cc_test_config['gperftools_libs'])
        perftools_debug_lib = var_to_list(cc_test_config['gperftools_debug_libs'])
        if heap_check:
            self.data['heap_check'] = heap_check

            if heap_check_debug:
                perftools_lib_list = perftools_debug_lib
            else:
                perftools_lib_list = perftools_lib

            self._add_hardcode_library(perftools_lib_list)


def cc_test(name,
            srcs=[],
            deps=[],
            warning='yes',
            defs=[],
            incs=[],
            export_incs=[],
            optimize=[],
            dynamic_link=None,
            testdata=[],
            extra_cppflags=[],
            extra_linkflags=[],
            export_dynamic=False,
            always_run=False,
            exclusive=False,
            heap_check=None,
            heap_check_debug=False,
            **kwargs):
    """cc_test target. """
    cc_test_target = CcTest(name,
                            srcs,
                            deps,
                            warning,
                            defs,
                            incs,
                            export_incs,
                            optimize,
                            dynamic_link,
                            testdata,
                            extra_cppflags,
                            extra_linkflags,
                            export_dynamic,
                            always_run,
                            exclusive,
                            heap_check,
                            heap_check_debug,
                            blade.blade,
                            kwargs)
    blade.blade.register_target(cc_test_target)


build_rules.register_function(cc_test)
