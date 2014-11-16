# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from distutils import log

__all__ = [
    'popen', 'system',
    'resolve_interpreter', 'get_postfix_name', 'get_python_version',
    'norm', 'to_filename',
    ]


def popen(cmd, verbose=0, **kwargs):
    if verbose:
        log.info('execute: %r' % cmd)

    proc = subprocess.Popen(
            cmd,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            **kwargs
        )

    for line in proc.stdout:
        log.debug(line.decode().rstrip())

    # FIXME: currently, error output write after stdout
    for line in proc.stderr:
        log.error(line.decode().rstrip())

    proc.wait()
    if verbose:
        log.info('return code: %r' % proc.returncode)
        log.info('executed: %r' % cmd)
    return proc.returncode


def system(cmd):
    proc = subprocess.Popen(
            cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
    outdata, errdata = proc.communicate()
    outdata = outdata.decode()
    errdata = errdata.decode()

    for line in errdata.splitlines():
        log.error(line.rstrip())

    return outdata


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


def get_postfix_name(python):
    name = "py%d.%d" % get_python_version(python)[:2]

    proc = subprocess.Popen(
            [python, '-c',
             'from distutils.util import get_platform; print(get_platform())'
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    out = out.decode()

    return name + '-' + out.strip()


def get_python_version(python):
    proc = subprocess.Popen(
            [python, '-c', 'import sys; print(tuple(sys.version_info))'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    out = out.decode()
    #FIXME: check proc.returncode
    #FIXME: eval is safe?
    return eval(out)


def norm(name):
    return name.replace('-','_')


def to_filename(project_name, project_version, postfix_name=None):
    filename = "%s-%s" % (norm(project_name), norm(project_version))
    if postfix_name:
        filename += '-' + postfix_name
    return filename
