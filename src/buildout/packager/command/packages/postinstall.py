# -*- coding: utf-8 -*-
import os
import sys
import subprocess


def main(app_dir):
    cwd = os.getcwd()
    pkg_dir = os.path.join(app_dir, 'packages')
    buildout = os.path.join('bin', 'buildout')
    cfg = 'buildout.cfg'
    bootstrap = os.path.join(pkg_dir, 'bootstrap-offline.py')
    bootstrap_opts = [
            '-d',  #use distribute
            '-c', cfg, #use config file to using offline-cache
            '--eggs', 'eggs', #use chached packages
                #use downloaded distribute_setup.py
            '--setup-source', os.path.join(pkg_dir, 'distribute_setup.py'),
                #use downloaded zc.buildout egg
            '--version', '1.6.3',
            ]
    env = dict([(k,os.environ[k]) for k in os.environ  # avoid PYTHONPATH
                if not k.startswith('PYTHON')])        # for installation

    os.chdir(app_dir)
    subprocess.check_call([sys.executable, bootstrap] + bootstrap_opts, env=env)
    subprocess.check_call([buildout, '-UNovc', cfg], env=env)
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

