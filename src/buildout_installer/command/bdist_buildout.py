# -*- coding: utf-8 -*-
from distutils.core import Command
import os, sys

if sys.platform == 'win32':
    import bdist_buildout_win32 as builder
else:
    import bdist_buildout_unix as builder


class bdist_buildout(Command):
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

    def run (self):
        self.run_command('bdist_buildout_prepare') #TODO: skip if prepared
        meta = self.distribution.metadata

        #### ŠÂ‹«•Ê‚Ìmake_package‚ğŒÄ‚Ño‚·
        if builder:
            builder.make_package(meta.name, meta.name, meta.name,
                                 self.build_dir,
                                 self.dist_dir,
                                 meta.version,
                                 meta.author,
                                 meta.url)

