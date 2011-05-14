# -*- coding: utf-8 -*-

## WARNING:
##
## pyinstaller_supoort is experimental.
## If you use pyinstaller, pyinstaller-1.5.zip file place same directory.
##

import os
import sys

pyinstaller_path = os.path.join(
                        os.path.dirname(__file__),
                        'pyinstaller-1.5.zip'
                    )
if os.path.exists(pyinstaller_path):
    PYINSTALLER_ENABLE = True
    sys.path.append(
            os.path.join(
                pyinstaller_path,
                'pyinstaller-1.5'
            )
        )
    import bindepend
    import pefile
else:
    PYINSTALLER_ENABLE = False


def find_depends(build_dir):
    if not PYINSTALLER_ENABLE:
        raise RuntimeError(
                "You can't use PyInstaller.\nPlease read document in '%s'" %
                os.path.abspath(__file__)
            )

    # search from build directory
    ltoc = []
    for dirpath, dirs, files in os.walk(build_dir):
        for fn in files:
            path = os.path.join(dirpath, fn)
            try:
                pefile.PE(path)
                ltoc.append((fn, path, "UNKNOWN"))
            except:
                pass

    bindepend.silent = True  # Suppress all informative messages from the dependency code
    bindepend.Dependencies(ltoc)
    results = []
    for name, path, typ in ltoc:
        if typ == "UNKNOWN":
            continue
        results.append([name, path])

    return results

