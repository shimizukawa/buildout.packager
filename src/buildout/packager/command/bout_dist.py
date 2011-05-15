# -*- coding: utf-8 -*-
from distutils.core import Command
import os
import sys
from utils import resolve_interpreter, get_postfix_name

if sys.platform == 'win32':
    from innosetup_builder import builder
else:
    from unix_builder import builder


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

    def run (self):
        cmd_name = 'bout_src'
        sub_cmd = self.reinitialize_command(cmd_name)
        for option in ('src_dir', 'build_base', 'dist_dir', 'include_python', 'python'):
            sub_cmd.initialized_options[option] = getattr(self, option)
        self.run_command(cmd_name) #TODO: skip if prepared

        postfix_name = get_postfix_name(self.python)
        build_dir = os.path.join(self.build_base, 'buildout-' + postfix_name)
        meta = self.distribution.metadata

        #### ä¬ã´ï ÇÃmake_packageÇåƒÇ—èoÇ∑
        builder(meta.name, meta.name, meta.name,
                build_dir,
                self.dist_dir,
                meta.version,
                meta.author,
                meta.url,
                postfix_name,
                self.verbose)

