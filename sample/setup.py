from setuptools import setup
from datetime import datetime

setup(
    name='Sphinx',
    version=datetime.now().strftime('1.0.7.alpha%Y%m%d'),
    author='Sphinx-users.jp',
    url='http://sphinx-users.jp',
    license='',
    #packages='.',
    #package_dir={'': '.'},
    #package_data={'': ['buildout.cfg']},
    #namespace_packages=[${repr($namespace_package)}],
    include_package_data=True,
)

