# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kirlent', 'kirlent.docutils']

package_data = \
{'': ['*']}

install_requires = \
['docutils>=0.17']

entry_points = \
{'console_scripts': ['kirlent2impressjs = '
                     'kirlent.docutils:publish_cmdline_impressjs',
                     'kirlent2revealjs = '
                     'kirlent.docutils:publish_cmdline_revealjs',
                     'rst2kirlenthtml5 = '
                     'kirlent.docutils:publish_cmdline_html5']}

setup_kwargs = {
    'name': 'kirlent-docutils',
    'version': '0.1.0',
    'description': 'Custom writers for docutils.',
    'long_description': 'kirlent_docutils is a set of tools\nfor generating impress.js and reveal.js presentations\nfrom restructured text documents.\n\nSince it aims to be compatible with any restructured text tool,\nit doesn\'t define its own directives\nand instead uses only standard `docutils`_ features.\n\nAt the moment, the tools are functional\nbut their usage and the slide markup might change.\nThis is also the reason why there is no documentation yet.\nYou can check out the files in the "examples" directory.\n\n.. _docutils: https://docutils.sourceforge.io/\n',
    'author': 'H. Turgut Uyar',
    'author_email': 'uyar@tekir.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tekir.org/kirlent_docutils/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
