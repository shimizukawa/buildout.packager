from setuptools import setup
from datetime import datetime

setup(
    name='SphinxInstaller',  # Package Name need unique name
    version=datetime.now().strftime('1.0.8-ja-%Y%m%d'),
    author='Sphinx-users.jp',
    url='http://sphinx-users.jp',
    license='',
    include_package_data=True,
    install_requires = [
        'Pillow',
        'sphinx',
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
        'sphinxjp.themecore',
        'sphinxjp.themes.bizstyle',
        'sphinxjp.themes.dotted',
        'sphinxjp.themes.htmlslide',
        'sphinxjp.themes.s6',
        'sphinxjp.themes.solarized',
        'sphinxjp.themes.sphinxjp',
        'sphinxjp.themes.trstyle',
        'sphinxjp.themes.impressjs',
    ],
    dependency_links = [
        "https://bitbucket.org/shimizukawa/pillow/downloads"
    ],
    options = {
        'bout_config': {
            'buildout_option': """\
                dependent-scripts = true
                interpreter = python
            """,
            'installer_name': 'Sphinx',  # default: Package Name
            'application_name': 'Sphinx',  # default: Package Name
            'vcs_packages': [
                'hg+http://bitbucket.org/shimizukawa/sphinx/@1.0.8-ja#egg=sphinx',
            ],
            'buildout_locallibs': [
                'Pillow = PIL==1.1.7',
            ],
        },
    },
)
