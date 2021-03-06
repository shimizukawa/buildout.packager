# -*- coding: utf-8 -*-
#from distutils.core import setup
from setuptools import setup, find_packages
import os

version = '0.0.1'
long_description = \
  open(os.path.join("src","buildout","packager","README.txt")).read() + \
  open(os.path.join("TODO.txt")).read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Environment :: Win32 (MS Windows)",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
#    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
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
     url='http://bitbucket.org/shimizukawa/buildout.packager/',
     license='Apache License 2.0',
     namespace_packages=['buildout'],
     packages=find_packages('src'),
     package_dir={'': 'src'},
     dependency_links=[
         'http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/',
     ],
     install_requires=[
         'setuptools',
         'py2exe',
          # -*- Extra requirements: -*-
     ],
     entry_points="""
         [distutils.commands]
         bout_src     = buildout.packager.command:bout_src
         bout_wininst = buildout.packager.command:bout_wininst
         bout_zip     = buildout.packager.command:bout_zip
     """,
)

