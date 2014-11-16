# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
import shutil
from distutils.core import Command

from .utils import resolve_interpreter, get_postfix_name, to_filename

# from unix_builder import builder


class bout_dist(Command):
    description = "build distribution"

    user_options = [
        ('build-base=', 'b',
         "base directory for build library"),
        ('src-dir=', 's',
         "directory to get buildout files in"
         "[default: src]"),
        ('dist-dir=', 'd',
         "directory to put the source distribution archive(s) in "
         "[default: dist]"),
        ('include-python', 'i',
         "include the Python interpreter. [default: False]"),
        ('python=', 'p',
         "include the specified Python interpreter. [default: %s]" % sys.executable),
        ]

    def initialize_options (self):
        self.src_dir = None
        self.build_base = None
        self.dist_dir = None
        self.include_python = False
        self.python = None
        self.compiler = None

    def finalize_options (self):
        if self.src_dir is None:
            self.src_dir = "src"
        if self.build_base is None:
            self.build_base = "build"
        if self.dist_dir is None:
            self.dist_dir = "dist"
        if self.python:
            self.include_python = True
            self.python = resolve_interpreter(self.python)
        else:
            self.python = sys.executable


class bout_wininst(bout_dist):
    description = "create a buildout installer for windows."

    user_options = bout_dist.user_options + [
        ('compiler=', 'c',
            "compiler to compile installer. [default: innosetup]"),
        ]

    def initialize_options(self):
        bout_dist.initialize_options(self)
        self.compiler = None

    def finalize_options (self):
        bout_dist.finalize_options(self)
        if self.compiler is None:
            self.compiler = 'innosetup'
        else:
            compiler = self.compiler + '_builder'
            __import__(compiler, globals(), locals(), level=1)

    def run (self):
        cmd_name = 'bout_src'
        sub_cmd = self.reinitialize_command(cmd_name)
        for option in ('src_dir', 'build_base', 'dist_dir', 'include_python', 'python'):
            sub_cmd.initialized_options[option] = getattr(self, option)
        self.run_command(cmd_name) #TODO: skip if prepared

        postfix_name = get_postfix_name(self.python)
        build_dir = os.path.join(self.build_base, 'buildout-' + postfix_name)
        meta = self.distribution.metadata
        options = dict(self.distribution.command_options.get('bout_config', {}))
        application_name = options.get('application_name',
                                       ('default', meta.name))[1]
        installer_name = options.get('installer_name',
                                     ('default', meta.name))[1]

        #### 環境別のmake_packageを呼び出す
        compiler = self.compiler + '_builder'
        builder = __import__(compiler, globals(), locals(), level=1)
        builder.builder(
                application_name,  # Application Name
                installer_name,    # Installer Name
                application_name,  # Install Default Target Dir
                build_dir,
                self.dist_dir,
                meta.version,
                meta.author,
                meta.url,
                postfix_name,
                self.verbose)


class bout_zip(bout_dist):
    description = "create a buildout zip installer."

    def run (self):
        cwd = os.getcwd()
        cmd_name = 'bout_src'
        sub_cmd = self.reinitialize_command(cmd_name)
        for option in ('src_dir', 'build_base', 'dist_dir', 'include_python', 'python'):
            sub_cmd.initialized_options[option] = getattr(self, option)
        self.run_command(cmd_name) #TODO: skip if prepared

        postfix_name = get_postfix_name(self.python)
        meta = self.distribution.metadata
        build_dir = os.path.join(
                cwd, self.build_base, 'buildout-' + postfix_name)
        pkg_dir = os.path.join(build_dir, 'packages')

        remove_list = []
        if os.name == 'nt':
            shutil.copy(os.path.join(pkg_dir, 'setup.bat'), build_dir)
            remove_list.append(os.path.join(build_dir, 'setup.bat'))

        zipfile_name = to_filename(meta.name, meta.version, postfix_name)
        filename = self.make_archive(
                os.path.join(self.dist_dir, zipfile_name), 'zip',
                root_dir=build_dir, base_dir=None)

        for f in remove_list:
            os.remove(f)

