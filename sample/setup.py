from setuptools import setup
from datetime import datetime

setup(
    name='SphinxInstaller',  # Package Name need unique name
    version=datetime.now().strftime('1.2.3.%Y%m%d'),
    author='Sphinx-users.jp',
    url='http://sphinx-users.jp',
    license='',
    include_package_data=True,
    install_requires = [
        'Pillow',
        'sphinx==1.2.3',
        'actdiag',
        'blockdiag',
        'nwdiag',
        'seqdiag',
        'sphinxcontrib-blockdiag',
        'sphinxcontrib-seqdiag',
        'sphinxcontrib-nwdiag',
        'sphinxcontrib-actdiag',
        'blockdiagcontrib-square',
        'blockdiagcontrib-qb',
        'blockdiagcontrib-class',
        'pypng',
        'sphinxjp.themes.bizstyle',
        'sphinxjp.themes.dotted',
        'sphinxjp.themes.htmlslide',
        'sphinxjp.themes.s6',
        'sphinxjp.themes.sphinxjp',
        'sphinxjp.themes.trstyle',
        'sphinxjp.themes.impressjs',
    ],
    options = {
        'bout_config': {
            'buildout_option': """\
                #dependent-scripts = true
                interpreter = sphinx-py
            """,
            #'installer_name': 'Sphinx',  # default: Package Name
            'application_name': 'Sphinx',  # default: Package Name
            'target_eggs': [
                'Sphinx==1.2.3'  # for generate script
            ],
            #'vcs_packages': [
            #    'hg+http://bitbucket.org/birkenfeld/sphinx#egg=sphinx',
            #],
        },
    },
)
