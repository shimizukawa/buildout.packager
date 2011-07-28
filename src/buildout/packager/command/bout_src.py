# -*- coding: utf-8 -*-
import os
import sys
import string
import shutil
import textwrap
from distutils.core import Command
from distutils import log
from utils import popen, resolve_interpreter, get_postfix_name

import py2exe_support
import pyinstaller_support


if py2exe_support.ENABLE:
    find_depends = py2exe_support.find_depends
elif pyinstaller_support.ENABLE:
    find_depends = pyinstaller_support.find_depends
else:
    raise RuntimeError("buildout.packager need install py2exe.")


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


def copy_depends(build_dir, dest_dir):
    log.info("Check dependencies.")

    for name, path in find_depends(build_dir):
        if path.lower().startswith(build_dir.lower()):
            continue
        log.info("copying dependency file: %s" % name)
        shutil.copy2(path, os.path.join(dest_dir, name))


def template(src, dst, **kw):
    f = open(src, 'rt')
    tmpl = f.read()
    f.close()
    output = string.Template(tmpl).safe_substitute(kw)
    f = open(dst, 'wt')
    f.write(output)
    f.close()


class bout_src(Command):
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
        self.initialized_options = {}
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

        invalid = object()
        for option in ('src_dir', 'build_base', 'dist_dir', 'include_python', 'python'):
            value = self.initialized_options.get(option, invalid)
            if value is not invalid:
                setattr(self, option, value)

    def run(self):
        meta = self.distribution.metadata
        options = dict(self.distribution.command_options['bout_config'])
        cwd = os.path.abspath(os.getcwd()) #FIXME: setup.py実行ディレクトリの取得をしたい
        build_dir = os.path.join(cwd, self.build_base, 'buildout-' + get_postfix_name(self.python))
        pkg_base_dir = os.path.join(os.path.dirname(__file__), 'packages')
        pkg_dir = os.path.join(build_dir, 'packages')
        cache_dir = build_dir
        eggs_dir = os.path.join(cache_dir, 'eggs')
        build_python_dir = os.path.join(build_dir, 'python')
        buildout_cmd = os.path.join('bin','buildout')

        if self.include_python:
            executable = os.path.join(build_python_dir, os.path.basename(self.python))
            log.info("bdist_src including Python Interpreter at '%s'", executable)
        else:
            if os.path.exists(build_python_dir):
                # TODO: implement bout_clean command and move this block.
                shutil.rmtree(build_python_dir)
            build_python_dir = None
            executable = sys.executable

        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir)
        for name in os.listdir(pkg_base_dir):
            #TODO: 前のパッケージの削除をするか？ 今はコピー済みpackagesに上書きしている。
            src = os.path.join(pkg_base_dir, name)
            if os.path.isfile(src):
                shutil.copy(src, os.path.join(pkg_dir, name))

        for name in ('buildout_pre.cfg', 'buildout.cfg'):
            template(
                    os.path.join(pkg_base_dir, name),
                    os.path.join(build_dir, name),
                    target_egg=meta.name,
                    buildout_option=textwrap.dedent(options['buildout_option'][1]))

        if not os.path.exists(eggs_dir):
            os.makedirs(eggs_dir)

        os.chdir(build_dir)

        # copy python files
        if build_python_dir and not os.path.exists(executable):
            copy_python(os.path.dirname(self.python), build_python_dir)

        # bootstrap and build
        log.info("bootstrap and build environment.")
        cmd = [executable, '-S', os.path.join(pkg_dir,'bootstrap2.py'), '-d', 'init']
        popen(cmd)
        cmd = [buildout_cmd, 'setup', cwd, 'bdist_egg', '-d', eggs_dir]
        popen(cmd)
        cmd = [buildout_cmd, '-UNc', 'buildout_pre.cfg']
        if self.verbose:
            cmd.append('-%s' % ('v' * self.verbose))
        popen(cmd)

        # finally
        os.chdir(cwd)

        # reomve non-packaging files/dirs
        log.info("remove unused files/dirs")
        for name in ['bin','develop-eggs','parts','buildout_pre.cfg','.installed.cfg']:
            path = os.path.join(build_dir, name)
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        # copy depends
        # TODO: copy depends when python-interpreter was not copied
        if build_python_dir:
            copy_depends(build_dir, build_python_dir)

