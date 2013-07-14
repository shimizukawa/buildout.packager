import os
import sys
bjoin = lambda *a: os.path.join(os.path.dirname(__file__), *a)

import site
site.addsitedir(bjoin('..', 'eggs'))
del site
del sys.modules['site']

from glob import glob
import ez_setup
ez_setup._install(sorted(glob(bjoin('../eggs/setuptools-*gz')))[-1])
del ez_setup
del glob

execfile(bjoin('bootstrap.py'))
