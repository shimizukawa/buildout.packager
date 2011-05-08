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
        ]

    def initialize_options (self):
        self.src_dir = None
        self.build_base = None
        self.dist_dir = None

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

        cmd = [sys.executable, os.path.join(pkg_dir,'bootstrap2.py'), 'init']
        popen(cmd)

        cmd = [os.path.join('bin','buildout'), '-UNc', 'buildout_pre.cfg']
        if self.verbose:
            cmd.append('-%s' % ('v' * self.verbose))
        popen(cmd)

        os.chdir(cwd)

        # reomve non-packaging files/dirs
        for name in ['bin','develop-eggs','parts','buildout_pre.cfg','.installed.cfg']:
            path = os.path.join(build_dir, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

