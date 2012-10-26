import os
import sys
import site
BASE = os.path.dirname(__file__)
site.addsitedir(os.path.join(BASE, 'eggs'))
del site
del sys.modules['site']
execfile(os.path.join(BASE, 'bootstrap.py'))
