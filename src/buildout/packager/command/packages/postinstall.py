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

    # ez_setup
    setuptools_src = sorted(glob(os.path.join(eggs_dir, 'setuptools-*gz')))[0]
    ez_setup = [
            sys.executable, '-c',
            "import ez_setup; "
            "ez_setup._install('%(setuptools_src)s'); "
            % locals()
            ]
    subprocess.check_call(ez_setup, cwd=pkg_dir, env=env)

    # bootstrap
    buildouts_src = sorted(glob(os.path.join(eggs_dir, 'zc.buildout-*gz')))[-1]
    cfg = 'buildout.cfg'
    bootstrap_cmd = [
            sys.executable, '-m', 'easy_install', buildouts_src,
            ]
    subprocess.check_call(bootstrap_cmd, cwd=app_dir, env=env)

    # buildout
    buildout_cmd = [
            sys.executable, '-c',
            "from zc.buildout.buildout import main; "
            "main(['-Uvc', '%(cfg)s']); "
            % locals()
            ]
    subprocess.check_call(buildout_cmd, cwd=app_dir, env=env)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))

    if not os.path.exists(path):
        print >>sys.stderr, '"%s" is not directory' % path
        sys.exit(-2)
    main(path)

