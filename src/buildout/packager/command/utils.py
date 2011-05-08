# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from distutils import log

__all__ = ['popen', 'resolve_interpreter', 'get_python_version']


def popen(cmd):
    proc = subprocess.Popen(
            cmd,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )

    for line in iter(proc.stdout.readline, ''):
        log.debug(line.rstrip())

    # FIXME: currently, error output write after stdout
    for line in iter(proc.stderr.readline, ''):
        log.error(line.rstrip())

    proc.wait()
    return proc.returncode


# resolve_interpreter function was copied from virtualenv.py and modified
def resolve_interpreter(exe):
    """
    If the executable given isn't an absolute path, search $PATH for the interpreter
    """
    if os.path.abspath(exe) != exe:
        paths = os.environ.get('PATH', '').split(os.pathsep)
        for path in paths:
            if os.path.exists(os.path.join(path, exe)):
                exe = os.path.join(path, exe)
                break
            elif os.path.exists(os.path.join(path, exe + '.exe')):
                exe = os.path.join(path, exe + '.exe')
                break
    if not os.path.exists(exe):
        log.fatal('The executable %s (from -p %s) does not exist' % (exe, exe))
        sys.exit(3)
    return exe


def get_python_version(python):
    proc = subprocess.Popen(
            [python, '-c', 'import sys; print sys.version_info'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    #FIXME: check proc.returncode
    #FIXME: eval is safe?
    return eval(out)

