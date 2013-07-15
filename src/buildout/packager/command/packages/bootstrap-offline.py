import os
bjoin = lambda *a: os.path.join(os.path.dirname(__file__), *a)

from glob import glob
import ez_setup
ez_setup._install(sorted(glob(bjoin('../eggs/setuptools-*gz')))[-1])
del ez_setup
del glob

import sys
import site
for d in [d for d in sys.path if 'site-packages' in d]:
    site.addsitedir(d)
del site
del sys

execfile(bjoin('bootstrap.py'))
