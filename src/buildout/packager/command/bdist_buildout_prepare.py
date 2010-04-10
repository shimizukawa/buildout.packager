# -*- coding: utf-8 -*-
from distutils.core import Command
import os, sys, shutil


class bdist_buildout_prepare(Command):
    description = "create a buildout installer"

    user_options = [
        ('src-dir=', 's',
         "directory to get buildout files in"
         "[default: src]"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) in "
         "[default: dist]"),
        ]

    def initialize_options (self):
        self.src_dir = None
        self.build_dir = None
        self.dist_dir = None

    def finalize_options (self):
        if self.src_dir is None:
            self.src_dir = "src"
        if self.build_dir is None:
            self.build_dir = "build"
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self):
        cwd = os.getcwd() #FIXME: setup.py実行ディレクトリの取得をしたい
        build_dir = os.path.join(cwd, self.build_dir)
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
        shutil.copy(os.path.join(cwd, 'buildout.cfg'), build_dir) #FIXME: buildout.cfg exist?

        if not os.path.exists(os.path.join(cache_dir,'download-cache')):
            os.makedirs(os.path.join(cache_dir,'download-cache'))
        if not os.path.exists(os.path.join(cache_dir,'eggs')):
            os.makedirs(os.path.join(cache_dir,'eggs'))

        os.chdir(build_dir)
        #FIXME! don't use os.system!
        os.system(sys.executable + ' ' + os.path.join(pkg_dir,'bootstrap2.py') + ' init')
        os.system(os.path.join('bin','buildout -Uv -c ' + os.path.join(pkg_dir,'buildout_pre.cfg')))
        shutil.rmtree('bin')
        shutil.rmtree('develop-eggs')
        shutil.rmtree('parts')
        os.chdir(cwd)

