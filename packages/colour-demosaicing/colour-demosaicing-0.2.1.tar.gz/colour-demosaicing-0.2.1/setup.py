# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_demosaicing',
 'colour_demosaicing.bayer',
 'colour_demosaicing.bayer.demosaicing',
 'colour_demosaicing.bayer.demosaicing.tests',
 'colour_demosaicing.bayer.tests']

package_data = \
{'': ['*'],
 'colour_demosaicing': ['examples/*',
                        'resources/colour-demosaicing-examples-datasets/*',
                        'resources/colour-demosaicing-tests-datasets/*']}

install_requires = \
['colour-science>=0.4.0',
 'imageio>=2,<3',
 'numpy>=1.19,<2',
 'scipy>=1.5,<2',
 'typing-extensions>=4,<5']

extras_require = \
{'development': ['biblib-simple',
                 'black',
                 'coverage!=6.3',
                 'coveralls',
                 'flake8',
                 'flynt',
                 'invoke',
                 'jupyter',
                 'mypy',
                 'pre-commit',
                 'pydata-sphinx-theme',
                 'pydocstyle',
                 'pytest',
                 'pytest-cov',
                 'pyupgrade',
                 'restructuredtext-lint',
                 'sphinx>=4,<5',
                 'sphinxcontrib-bibtex',
                 'toml',
                 'twine'],
 'plotting': ['matplotlib>=3.2,!=3.5.0,!=3.5.1'],
 'read-the-docs': ['matplotlib>=3.2,!=3.5.0,!=3.5.1',
                   'pydata-sphinx-theme',
                   'sphinxcontrib-bibtex']}

setup_kwargs = {
    'name': 'colour-demosaicing',
    'version': '0.2.1',
    'description': 'CFA (Colour Filter Array) Demosaicing Algorithms for Python',
    'long_description': "Colour - Demosaicing\n====================\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://img.shields.io/github/workflow/status/colour-science/colour-demosaicing/Continuous%20Integration?label=actions&logo=github&style=flat-square\n    :target: https://github.com/colour-science/colour-demosaicing/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-demosaicing/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-demosaicing\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/984900e3a85e40239a0f8f633dd1ebcb/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-demosaicing\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-demosaicing.svg?style=flat-square\n    :target: https://pypi.org/project/colour-demosaicing\n    :alt: Package Version\n\n.. end-badges\n\nA `Python <https://www.python.org/>`__ package implementing various\nCFA (Colour Filter Array) demosaicing algorithms and related utilities.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n..  image:: https://raw.githubusercontent.com/colour-science/colour-demosaicing/master/docs/_static/Demosaicing_001.png\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 2\n\n.. sectnum::\n\nFeatures\n--------\n\nThe following CFA (Colour Filter Array) demosaicing algorithms are implemented:\n\n- Bilinear\n- Malvar (2004)\n- DDFAPD - Menon (2007)\n\nExamples\n^^^^^^^^\n\nVarious usage examples are available from the\n`examples directory <https://github.com/colour-science/colour-demosaicing/tree/master/colour_demosaicing/examples>`__.\n\nUser Guide\n----------\n\nInstallation\n^^^^^^^^^^^^\n\nBecause of their size, the resources dependencies needed to run the various\nexamples and unit tests are not provided within the Pypi package. They are\nseparately available as\n`Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`__\nwhen cloning the\n`repository <https://github.com/colour-science/colour-demosaicing>`__.\n\nPrimary Dependencies\n~~~~~~~~~~~~~~~~~~~~\n\n**Colour - Demosaicing** requires various dependencies in order to run:\n\n- `python >= 3.8, < 4 <https://www.python.org/download/releases/>`__\n- `colour-science <https://pypi.org/project/colour-science/>`__\n\nPypi\n~~~~\n\nOnce the dependencies are satisfied, **Colour - Demosaicing** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-demosaicing>`__ by\nissuing this command in a shell::\n\n    pip install --user colour-demosaicing\n\nThe overall development dependencies are installed as follows::\n\n    pip install --user 'colour-demosaicing[development]'\n\nContributing\n^^^^^^^^^^^^\n\nIf you would like to contribute to `Colour - Demosaicing <https://github.com/colour-science/colour-demosaicing>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n^^^^^^^^^^^^\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-demosaicing/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nAPI Reference\n-------------\n\nThe main technical reference for `Colour - Demosaicing <https://github.com/colour-science/colour-demosaicing>`__\nis the `API Reference <https://colour-demosaicing.readthedocs.io/en/latest/reference.html>`__.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nContact & Social\n----------------\n\nThe *Colour Developers* can be reached via different means:\n\n- `Email <mailto:colour-developers@colour-science.org>`__\n- `Facebook <https://www.facebook.com/python.colour.science>`__\n- `Github Discussions <https://github.com/colour-science/colour-demosaicing/discussions>`__\n- `Gitter <https://gitter.im/colour-science/colour>`__\n- `Twitter <https://twitter.com/colour_science>`__\n\nAbout\n-----\n\n| **Colour - Demosaicing** by Colour Developers\n| Copyright 2015 Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-demosaicing <https://github.com/colour-science/colour-demosaicing>`__\n",
    'author': 'Colour Developers',
    'author_email': 'colour-developers@colour-science.org',
    'maintainer': 'Colour Developers',
    'maintainer_email': 'colour-developers@colour-science.org',
    'url': 'https://www.colour-science.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
