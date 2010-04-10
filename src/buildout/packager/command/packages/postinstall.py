# -*- coding: utf-8 -*-
from distutils.core import Command
import os, sys, shutil

def main(app_dir):
    cwd = os.getcwd()
    pkg_dir = os.path.join(app_dir, 'packages')

    os.chdir(app_dir)
    #FIXME! don't use os.system!
    os.system(sys.executable + ' ' + os.path.join(pkg_dir,'bootstrap2.py') + ' init')
    os.system(os.path.join('bin','buildout -v -c ' + os.path.join(pkg_dir,'buildout_post.cfg')))
    os.chdir(cwd)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = os.path.dirname(os.path.dirname(sys.argv[0]))

    if not os.path.exists(path):
        print >>sys.stderr, '"%s" is not directory' % sys.argv[1]
        sys.exit(-2)
    main(path)

