from setuptools import setup
from datetime import datetime

setup(
    name='SphinxInstaller',  # Package Name need unique name
    version=datetime.now().strftime('1.0.7alpha-%Y%m%d'),
    author='Sphinx-users.jp',
    url='http://sphinx-users.jp',
    license='',
    #packages='.',
    #package_dir={'': '.'},
    #package_data={'': ['buildout.cfg']},
    #namespace_packages=[${repr($namespace_package)}],
    include_package_data=True,
    install_requires = [
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
        'PIL',
        'sphinxjp.themecore',
        'sphinxjp.themes.biz_blue_simple',
        'sphinxjp.themes.bizstyle',
        'sphinxjp.themes.htmlslide',
        'sphinxjp.themes.s6',
        'sphinxjp.themes.sphinxjp',
    ],
    options = {
        'bout_config': {
            'buildout_option': """\
                dependent-scripts = true
                interpreter = python
                initialization =
                    import sys, types
                    sys.modules['PIL'] = types.ModuleType('PIL')
                    sys.modules['PIL'].Image = __import__('Image')
            """,
            'installer_name': 'Sphinx',  # default: Package Name
            'application_name': 'Sphinx',  # default: Package Name
            'vcs_packages': [
                'hg+http://bitbucket.org/shimizukawa/sphinx/@1.0.7-ja#egg=sphinx',
            ],
        },
    },
)
