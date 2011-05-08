# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
from distutils.core import Command
from distutils import log


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


def copy_python(src_python_dir, build_python_dir):
    if os.path.exists(build_python_dir):
        return

    log.info("Copying python files.")

    for name in ('libs', 'DLLs', 'include'):
        shutil.copytree(
                os.path.join(src_python_dir, name),
                os.path.join(build_python_dir, name))

    # copy Lib exclude site-packages
    shutil.copytree(
            os.path.join(src_python_dir, 'Lib'),
            os.path.join(build_python_dir, 'Lib'),
            ignore=shutil.ignore_patterns('site-packages'))
            #FIXME: ignore kw accept after python-2.6

    # make site-packages and copy README.txt
    site_packages = os.path.join(build_python_dir, 'Lib', 'site-packages')
    os.mkdir(site_packages)
    placeholder = os.path.join(src_python_dir, 'Lib', 'site-packages', 'README.txt')
    if os.path.exists(placeholder):
        shutil.copy2(placeholder, site_packages)
    else:
        open(os.path.join(site_packages, 'README.txt'), 'w').close()

    # copy files at python root
    for filename in os.listdir(src_python_dir):
        path = os.path.join(src_python_dir, filename)
        if os.path.isfile(path):
            shutil.copy2(path, build_python_dir)


class bdist_buildout_prepare(Command):
    description = "create a buildout installer"

    user_options = [
        ('build-base=', 'b',
         "base directory for build library"),
        ('src-dir=', 's',
         "directory to get buildout files in"
         "[default: src]"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) in "
         "[default: dist]"),
        ('python', 'p',
         "include the Python interpreter. default is not include."),
        ]

    def initialize_options (self):
        self.src_dir = None
        self.build_base = None
        self.dist_dir = None
        self.python = False

    def finalize_options (self):
        if self.src_dir is None:
            self.src_dir = "src"
        if self.build_base is None:
            self.build_base = "build"
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self):
        cwd = os.getcwd() #FIXME: setup.py実行ディレクトリの取得をしたい
        build_dir = os.path.join(cwd, self.build_base, 'buildout')
        pkg_base_dir = os.path.join(os.path.dirname(__file__), 'packages')
        pkg_dir = os.path.join(build_dir, 'packages')
        cache_dir = os.path.join(build_dir,'cache')
        build_python_dir = os.path.join(build_dir, 'python')
        executable = os.path.join(build_python_dir, 'python.exe')

        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir)
        for name in os.listdir(pkg_base_dir):
            #TODO: 前のパッケージの削除をするか？ 今はコピー済みpackagesに上書きしている。
            src = os.path.join(pkg_base_dir, name)
            if os.path.isfile(src):
                shutil.copy(src, os.path.join(pkg_dir, name))
            if os.path.split(src)[1] in ('buildout_pre.cfg', 'buildout_post.cfg'):
                shutil.copy(src, os.path.join(build_dir, name)) #FIXME: check overwriting
        shutil.copy(os.path.join(cwd, 'buildout.cfg'), build_dir) #FIXME: buildout.cfg exist?

        if not os.path.exists(os.path.join(cache_dir,'download-cache')):
            os.makedirs(os.path.join(cache_dir,'download-cache'))
        if not os.path.exists(os.path.join(cache_dir,'eggs')):
            os.makedirs(os.path.join(cache_dir,'eggs'))

        os.chdir(build_dir)

        # copy python files
        # TODO: use option's specified python instead of sys.prefix
        copy_python(sys.prefix, build_python_dir)

        # bootstrap and build
        cmd = [executable, '-S', os.path.join(pkg_dir,'bootstrap2.py'), '-d', 'init']
        popen(cmd)
        cmd = [os.path.join('bin','buildout'), '-UNc', 'buildout_pre.cfg']
        if self.verbose:
            cmd.append('-%s' % ('v' * self.verbose))
        popen(cmd)

        # finally
        os.chdir(cwd)

        # reomve non-packaging files/dirs
        for name in ['bin','develop-eggs','parts','buildout_pre.cfg','.installed.cfg']:
            path = os.path.join(build_dir, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

