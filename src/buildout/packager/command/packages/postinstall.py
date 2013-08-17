# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from glob import glob


def main(app_dir):
    cwd = os.getcwd()
    pkg_dir = os.path.join(app_dir, 'packages')
    eggs_dir = os.path.join(app_dir, 'eggs')
    env = dict([(k,os.environ[k]) for k in os.environ  # avoid PYTHONPATH
                if not k.startswith('PYTHON')])        # for installation

    setuptools_src = sorted(glob(os.path.join(eggs_dir, 'setuptools-*gz')))[-1]
    easy_install = ['easy_install', '-U', setuptools_src]

    buildout = os.path.join('bin', 'buildout')
    cfg = 'buildout.cfg'
    bootstrap = os.path.join(pkg_dir, 'bootstrap.py')
    bootstrap_opts = [
            '-c', cfg,  #use config file to using offline-cache
            '--version', '2.2.0',  # no check with internet
            ]

    os.chdir(app_dir)
    subprocess.check_call([sys.executable, '-m'] + easy_install, env=env)
    subprocess.check_call([sys.executable, bootstrap] + bootstrap_opts, env=env)
    subprocess.check_call([buildout, '-UNvc', cfg], env=env)
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

