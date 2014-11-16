# -*- coding: utf-8 -*-

import os
import sys

if sys.version_info < (3, 0):

    try:
        from py2exe import build_exe, py2exe_util
        ENABLE = True
    except:
        ENABLE = False


    def find_depends(build_dir):
        if not ENABLE:
            raise RuntimeError("You can't use py2exe.\nPlease install py2exe.")

        sysdir = py2exe_util.get_sysdir()
        windir = py2exe_util.get_windir()
        syspath = os.environ['PATH']
        paths = ';'.join([sysdir, windir, syspath])

        # search from build directory
        results = []
        for dirpath, dirs, files in os.walk(build_dir):
            for fn in files:
                path = os.path.join(dirpath, fn)
                try:
                    fileset = build_exe.bin_depends(
                            paths, [path], build_exe.EXCLUDED_DLLS)
                    for fs in fileset:
                        results.extend(f for f in fs if f not in results)
                except:
                    pass

        for f in results:
            for fs in build_exe.bin_depends(paths, [f], build_exe.EXCLUDED_DLLS):
                results.extend(f for f in fs if f not in results)

        return ((os.path.split(x)[1], x) for x in results)

else:

    try:
        from py2exe import dllfinder
        ENABLE = True
    except:
        ENABLE = False


    def find_depends(build_dir):
        if not ENABLE:
            raise RuntimeError("You can't use py2exe.\nPlease install py2exe.")

        # search from build directory
        results = set()
        for dirpath, dirs, files in os.walk(build_dir):
            files = [
                f for f in files
                if f.lower().endswith(('.dll', '.pyd', '.exe'))
            ]
            for fn in files:
                path = os.path.join(dirpath, fn)
                scanner = dllfinder.Scanner()
                scanner.add_dll(path)
                results.update(scanner.real_dlls())


        return ((os.path.split(x)[1], x) for x in results)
