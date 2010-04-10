distutils extension module - create an buildout-based installer.

    zc.buildout is a Python-based build system for creating, assembling and
    deploying applications from multiple parts, some of which may be
    non-Python-based. It lets you create a buildout configuration and
    reproduce the same software later.  -- http://www.buildout.org/

buildout.packager creates single-file installers for an buildout-environment
along with all dependencies, which can be used without network access.


Requirements
------------

* Python 2.5 or later

* `InnoSetup <http://www.innosetup.com/>`_ for Windows installer


Dependencies
------------

* `setuptools <http://pypi.python.org/pypi/setuptools>`_ or
  `distribute <http://pypi.python.org/pypi/distribute>`_

* `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_


Features
--------

* You can create an installer reproducing zc.buildout environment.

* installer metadata over setup() metadata


Limitations
-----------

* The installer doesn't bundle Python interpreter.

* Not implemented for Unix environment.


An example
----------

setup.py::

    from setuptools import setup
    setup(
        name='Sphinx',
        version='1.0',
    )

buildout.cfg::

    [buildout]
    parts = app

    [app]
    recipe = zc.recipe.egg
    eggs =
        Sphinx


Do the command `python setup.py bdist_buildout`.
Then you get the installation file named `dist\Sphinx-1.0-py2.6-win32.exe`.


History
-------

0.0.1
~~~~~
* first release

