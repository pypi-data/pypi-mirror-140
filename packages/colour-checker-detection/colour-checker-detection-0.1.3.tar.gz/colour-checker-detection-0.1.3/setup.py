# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_checker_detection',
 'colour_checker_detection.detection',
 'colour_checker_detection.detection.tests']

package_data = \
{'': ['*'],
 'colour_checker_detection': ['examples/*',
                              'resources/colour-checker-detection-examples-datasets/*',
                              'resources/colour-checker-detection-tests-datasets/*']}

install_requires = \
['colour-science>=0.4.0',
 'imageio>=2,<3',
 'numpy>=1.19,<2',
 'opencv-python>=4,<5',
 'scipy>=1.5,<2',
 'typing-extensions>=4,<5']

extras_require = \
{'development': ['biblib-simple',
                 'black',
                 'coverage',
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
    'name': 'colour-checker-detection',
    'version': '0.1.3',
    'description': 'Colour checker detection with Python',
    'long_description': "Colour - Checker Detection\n==========================\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://img.shields.io/github/workflow/status/colour-science/colour-checker-detection/Continuous%20Integration?label=actions&logo=github&style=flat-square\n    :target: https://github.com/colour-science/colour-checker-detection/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-checker-detection/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-checker-detection\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/c543bc30229347cdaea00aadd3f79499/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-checker-detection\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-checker-detection.svg?style=flat-square\n    :target: https://pypi.org/project/colour-checker-detection\n    :alt: Package Version\n\n.. end-badges\n\n\nA `Python <https://www.python.org/>`__ package implementing various colour\nchecker detection algorithms and related utilities.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n..  image:: https://raw.githubusercontent.com/colour-science/colour-checker-detection/master/docs/_static/ColourCheckerDetection_001.png\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 2\n\n.. sectnum::\n\nFeatures\n--------\n\nThe following colour checker detection algorithms are implemented:\n\n- Segmentation\n\nExamples\n^^^^^^^^\n\nVarious usage examples are available from the\n`examples directory <https://github.com/colour-science/colour-checker-detection/tree/master/colour_checker_detection/examples>`__.\n\nUser Guide\n----------\n\nInstallation\n^^^^^^^^^^^^\n\nBecause of their size, the resources dependencies needed to run the various\nexamples and unit tests are not provided within the Pypi package. They are\nseparately available as\n`Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`__\nwhen cloning the\n`repository <https://github.com/colour-science/colour-checker-detection>`__.\n\nPrimary Dependencies\n~~~~~~~~~~~~~~~~~~~~\n\n**Colour - Checker Detection** requires various dependencies in order to run:\n\n- `python >= 3.8, < 4 <https://www.python.org/download/releases/>`__\n- `colour-science >= 4 <https://pypi.org/project/colour-science/>`__\n- `imageio >= 2, < 3 <https://imageio.github.io/>`__\n- `numpy >= 1.19, < 2 <https://pypi.org/project/numpy/>`__\n- `opencv-python >= 4, < 5 <https://pypi.org/project/opencv-python/>`__\n- `scipy >= 1.5, < 2 <https://pypi.org/project/scipy/>`__\n\nPypi\n~~~~\n\nOnce the dependencies are satisfied, **Colour - Checker Detection** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-checker-detection>`__ by\nissuing this command in a shell::\n\n    pip install --user colour-checker-detection\n\nThe overall development dependencies are installed as follows::\n\n    pip install --user 'colour-checker-detection[development]'\n\nContributing\n^^^^^^^^^^^^\n\nIf you would like to contribute to `Colour - Checker Detection <https://github.com/colour-science/colour-checker-detection>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n^^^^^^^^^^^^\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-checker-detection/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nAPI Reference\n-------------\n\nThe main technical reference `Colour - Checker Detection <https://github.com/colour-science/colour-checker-detection>`__\nis the `API Reference <https://colour-checker-detection.readthedocs.io/en/latest/reference.html>`__.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nContact & Social\n----------------\n\nThe *Colour Developers* can be reached via different means:\n\n- `Email <mailto:colour-developers@colour-science.org>`__\n- `Facebook <https://www.facebook.com/python.colour.science>`__\n- `Github Discussions <https://github.com/colour-science/colour-checker-detection/discussions>`__\n- `Gitter <https://gitter.im/colour-science/colour>`__\n- `Twitter <https://twitter.com/colour_science>`__\n\nAbout\n-----\n\n| **Colour - Checker Detection** by Colour Developers\n| Copyright 2018 Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-checker-detection <https://github.com/colour-science/colour-checker-detection>`__\n",
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
