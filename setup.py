# -*- coding: utf-8 -*-
#from distutils.core import setup
from setuptools import setup
import os

version = '0.0.1'
long_description = \
  open(os.path.join("src","buildout","packager","README.txt")).read() + \
  open(os.path.join("TODO.txt")).read()

classifiers = [
   "Development Status :: 4 - Beta",
#   "Environment :: Win32 (MS Windows)",
   "Intended Audience :: Developers",
   "License :: OSI Approved :: Python Software Foundation License",
#   "Operating System :: Microsoft :: Windows :: Windows NT/2000",
   "Programming Language :: Python",
   "Topic :: Software Development :: Build Tools",
   "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='buildout.packager',
    version=version,
    description='buildout.packager generate installer from setup.py and buildout.cfg files.',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['zc.buildout','installer'],
    author='Takayuki SHIMIZUKAWA',
    author_email='shimizukawa at gmail.com',
    url='http://svn.freia.jp/open/buildout.packager/',
    license='PSL',
    package_dir={'': 'src'},
    install_requires=[
       'setuptools',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
       [distutils.commands]
       bdist_buildout = buildout.packager.command.bdist_buildout:bdist_buildout
       bdist_buildout_prepare = buildout.packager.command.bdist_buildout_prepare:bdist_buildout_prepare
    """,
)

