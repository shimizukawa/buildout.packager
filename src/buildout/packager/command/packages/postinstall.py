# -*- coding: utf-8 -*-
import os
import sys
import subprocess


def main(app_dir):
    cwd = os.getcwd()
    pkg_dir = os.path.join(app_dir, 'packages')
    bootstrap = os.path.join(pkg_dir, 'bootstrap2.py')
    buildout = os.path.join('bin', 'buildout')

    os.chdir(app_dir)
    subprocess.check_call([sys.executable, bootstrap, '-d', 'init'])
    subprocess.check_call([buildout, '-UNovc', 'buildout_post.cfg'])
    os.chdir(cwd)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

    if not os.path.exists(path):
        print >>sys.stderr, '"%s" is not directory' % path
        sys.exit(-2)
    main(path)

