# -*- coding: utf-8 -*-
import os
import sys
import string
import shutil
import textwrap
import hashlib
import tempfile
from distutils.core import Command
from distutils import log

import setuptools.archive_util

from utils import popen, system, resolve_interpreter, get_postfix_name
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
        dist_path = os.path.join(dest_dir, name)
        if os.path.exists(dist_path):
            if hashlib.md5(open(path, 'rb').read()).digest() != \
               hashlib.md5(open(dist_path, 'rb').read()).digest():
                shutil.remove(dist_path)
                shutil.copy2(path, dist_path)
            else:
                log.info("%s is not changed. skipped." % name)
        else:
            shutil.copy2(path, dist_path)


def template(src, dst, **kw):
    f = open(src, 'rt')
    tmpl = f.read()
    f.close()
    output = string.Template(tmpl).safe_substitute(kw)
    f = open(dst, 'wt')
    f.write(output)
    f.close()


def pickup_distributed_archive(fullname, dist_dir):
    for name in os.listdir(dist_dir):
        if name.lower().startswith(fullname.lower()):
            return name  #FIXME: find best_match package
    return None  # no package found


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
        options = dict(self.distribution.command_options.get('bout_config', {}))
        cwd = os.path.abspath(os.getcwd()) #FIXME: setup.py実行ディレクトリの取得をしたい
        build_dir = os.path.join(cwd, self.build_base, 'buildout-' + get_postfix_name(self.python))
        repos_dir = os.path.join(cwd, self.build_base, 'buildout-repos')
        pkg_base_dir = os.path.join(os.path.dirname(__file__), 'packages')
        pkg_dir = os.path.join(build_dir, 'packages')
        cache_dir = build_dir
        eggs_dir = os.path.join(cache_dir, 'eggs')
        eggs_dist_dir = os.path.join(cache_dir, 'eggs', 'dist')
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

        if 'vcs_packages' in options:
            vcs_packages = options['vcs_packages'][1]
        else:
            vcs_packages = []

        target_eggs = options.get('target_eggs', ['', []])[1]
        target_eggs.insert(0, meta.name)

        if 'buildout_option' in options:
            buildout_option = textwrap.dedent(options['buildout_option'][1])
        else:
            buildout_option = ''

        if 'buildout_locallibs' in options:
            buildout_locallibs = options['buildout_locallibs'][1]
        else:
            buildout_locallibs = []

        kw = dict(
            target_eggs='\n'.join('    '+x for x in target_eggs),
            buildout_option=buildout_option,
            buildout_locallibs='\n'.join(buildout_locallibs),
            vcs_extend_develop='\n'.join('    '+x for x in vcs_packages),
            repos_dir=repos_dir,
        )

        template(
                os.path.join(pkg_base_dir, 'buildout_pre.cfg'),
                os.path.join(build_dir, 'buildout_pre.cfg'),
                **kw
                )

        if not os.path.exists(eggs_dir):
            os.makedirs(eggs_dir)

        os.chdir(build_dir)

        # copy python files
        if build_python_dir and not os.path.exists(executable):
            copy_python(os.path.dirname(self.python), build_python_dir)

        # ez_setup
        log.info("install setuptools.")
        cmd = [executable, os.path.join(pkg_dir,'ez_setup.py')]
        errcode = popen(cmd, self.verbose, cwd=tempfile.gettempdir())
        if errcode:
            raise RuntimeError('command return error code:', errcode, cmd)


        # zc.buildout
        log.info("install zc.buildout.")
        cmd = [executable, '-m', 'easy_install', 'zc.buildout']
        errcode = popen(cmd, self.verbose)
        if errcode:
            raise RuntimeError('command return error code:', errcode, cmd)

        # bootstrap
        log.info("bootstrap and build environment.")
        if os.path.exists(os.path.join(build_dir, 'buildout.cfg')):
            # if already exist 'buildout.cfg' bootstrap.py cause error.
            os.remove(os.path.join(build_dir, 'buildout.cfg'))
        cmd = [executable,
               '-c', 'from zc.buildout.buildout import main; main()',
               '-U', 'init']
        errcode = popen(cmd, self.verbose)
        if errcode:
            raise RuntimeError('command return error code:', errcode, cmd)

        # build target egg
        cmd = [buildout_cmd,
               '-Uc', 'buildout_pre.cfg',
               'setup', cwd, 'bdist_egg', '-d', eggs_dir,
               ]
        errcode = popen(cmd, self.verbose)
        if errcode:
            raise RuntimeError('command return error code:', errcode, cmd)

        # buildout setup
        cmd = [buildout_cmd, '-Uc', 'buildout_pre.cfg']
        if self.verbose:
            cmd.append('-%s' % ('v' * self.verbose))
        errcode = popen(cmd, self.verbose)
        if errcode:
            raise RuntimeError('command return error code:', errcode, cmd)

        # build vcs packages
        for url in vcs_packages:
            dummy, pkg = url.split('#egg=')
            path = os.path.join(repos_dir, pkg)

            # make egg file
            cmd = [buildout_cmd,
                   '-c', 'buildout_pre.cfg',
                   'setup', path, 'bdist_egg', '-d', eggs_dist_dir
                   ]
            errcode = popen(cmd, self.verbose)
            if errcode:
                raise RuntimeError('command return error code:', errcode, cmd)

            # get package fullname and extract egg
            cmd = [buildout_cmd,
                   '-c', 'buildout_pre.cfg',
                   '-q', 'setup', path, '--fullname'
                   ]
            fullname = system(cmd).strip()
            filename = pickup_distributed_archive(fullname, eggs_dist_dir)
            # dist_file is FILE always.
            dist_file = os.path.join(eggs_dist_dir, filename)
            dest_dir = os.path.join(eggs_dir, filename)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            setuptools.archive_util.unpack_archive(dist_file, dest_dir)

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

        # buildout.cfg for installer
        template(
                os.path.join(pkg_base_dir, 'buildout.cfg'),
                os.path.join(build_dir, 'buildout.cfg'),
                **kw
                )

        # copy depends
        # TODO: copy depends when python-interpreter was not copied
        if build_python_dir:
            copy_depends(build_dir, build_python_dir)

