from setuptools import setup
from datetime import datetime

setup(
    name='SphinxInstaller',
    version=datetime.now().strftime('1.0.7.alpha%Y%m%d'),
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
                initialization =
                    import sys, types
                    sys.modules['PIL'] = types.ModuleType('PIL')
                    sys.modules['PIL'].Image = __import__('Image')
                interpreter = python
            """,
            'package_name': 'Sphinx',
        },
    },
)
