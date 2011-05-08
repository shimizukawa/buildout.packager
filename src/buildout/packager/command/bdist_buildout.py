# -*- coding: utf-8 -*-
from distutils.core import Command
import os
import sys
from utils import resolve_interpreter, get_python_version, get_postfix_name

if sys.platform == 'win32':
    import bdist_buildout_win32 as builder
else:
    import bdist_buildout_unix as builder


class bdist_buildout(Command):
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

    def run (self):
        cmd_name = 'bdist_buildout_prepare'
        sub_cmd = self.reinitialize_command(cmd_name)
        for option in ('src_dir', 'build_base', 'dist_dir', 'include_python', 'python'):
            setattr(sub_cmd, option, getattr(self, option))
        self.run_command(cmd_name) #TODO: skip if prepared

        build_dir = os.path.join(self.build_base, 'buildout-' + get_postfix_name(self.python))
        meta = self.distribution.metadata

        python_version = get_python_version(self.python)

        #### ���ʂ�make_package���Ăяo��
        if builder:
            builder.make_package(meta.name, meta.name, meta.name,
                                 build_dir,
                                 self.dist_dir,
                                 meta.version,
                                 meta.author,
                                 meta.url,
                                 python_version,
                                 self.verbose)

