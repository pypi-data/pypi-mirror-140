# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colour_hdri',
 'colour_hdri.calibration',
 'colour_hdri.calibration.tests',
 'colour_hdri.exposure',
 'colour_hdri.exposure.tests',
 'colour_hdri.generation',
 'colour_hdri.generation.tests',
 'colour_hdri.models',
 'colour_hdri.models.datasets',
 'colour_hdri.models.tests',
 'colour_hdri.plotting',
 'colour_hdri.process',
 'colour_hdri.process.tests',
 'colour_hdri.recovery',
 'colour_hdri.recovery.tests',
 'colour_hdri.sampling',
 'colour_hdri.sampling.tests',
 'colour_hdri.tonemapping',
 'colour_hdri.tonemapping.global_operators',
 'colour_hdri.tonemapping.global_operators.tests',
 'colour_hdri.utilities',
 'colour_hdri.utilities.tests']

package_data = \
{'': ['*'],
 'colour_hdri': ['examples/*', 'resources/colour-hdri-tests-datasets/*']}

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
                 'restructuredtext-lint',
                 'sphinx>=4,<5',
                 'sphinxcontrib-bibtex',
                 'toml',
                 'twine'],
 'optional': ['colour-demosaicing>=0.2.0'],
 'plotting': ['matplotlib>=3.2,!=3.5.0,!=3.5.1'],
 'read-the-docs': ['matplotlib>=3.2,!=3.5.0,!=3.5.1',
                   'pydata-sphinx-theme',
                   'sphinxcontrib-bibtex']}

setup_kwargs = {
    'name': 'colour-hdri',
    'version': '0.2.0',
    'description': 'HDRI / Radiance image processing algorithms for Python',
    'long_description': "Colour - HDRI\n=============\n\n.. start-badges\n\n|actions| |coveralls| |codacy| |version|\n\n.. |actions| image:: https://img.shields.io/github/workflow/status/colour-science/colour-hdri/Continuous%20Integration?label=actions&logo=github&style=flat-square\n    :target: https://github.com/colour-science/colour-hdri/actions\n    :alt: Develop Build Status\n.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-hdri/develop.svg?style=flat-square\n    :target: https://coveralls.io/r/colour-science/colour-hdri\n    :alt: Coverage Status\n.. |codacy| image:: https://img.shields.io/codacy/grade/290ad2c23b0749b99a1d548ca47d9062/develop.svg?style=flat-square\n    :target: https://www.codacy.com/app/colour-science/colour-hdri\n    :alt: Code Grade\n.. |version| image:: https://img.shields.io/pypi/v/colour-hdri.svg?style=flat-square\n    :target: https://pypi.org/project/colour-hdri\n    :alt: Package Version\n\n.. end-badges\n\nA `Python <https://www.python.org/>`__ package implementing various\nHDRI / Radiance image processing algorithms.\n\nIt is open source and freely available under the\n`New BSD License <https://opensource.org/licenses/BSD-3-Clause>`__ terms.\n\n..  image:: https://raw.githubusercontent.com/colour-science/colour-hdri/master/docs/_static/Radiance_001.png\n\n.. contents:: **Table of Contents**\n    :backlinks: none\n    :depth: 2\n\n.. sectnum::\n\nFeatures\n--------\n\nThe following features are available:\n\n- HDRI / Radiance Image Generation\n- Debevec (1997) Camera Response Function Computation\n- Grossberg (2003) Histogram Based Image Sampling\n- Variance Minimization Light Probe Sampling\n- Global Tonemapping Operators\n- Adobe DNG SDK Colour Processing\n- Absolute Luminance Calibration\n- Digital Still Camera (DSC) Exposure Model\n- Raw Processing Helpers\n\nExamples\n^^^^^^^^\n\nVarious usage examples are available from the\n`examples directory <https://github.com/colour-science/colour-hdri/tree/master/colour_hdri/examples>`__.\n\nUser Guide\n----------\n\nInstallation\n^^^^^^^^^^^^\n\nBecause of their size, the resources dependencies needed to run the various\nexamples and unit tests are not provided within the Pypi package. They are\nseparately available as\n`Git Submodules <https://git-scm.com/book/en/v2/Git-Tools-Submodules>`__\nwhen cloning the\n`repository <https://github.com/colour-science/colour-hdri>`__.\n\nPrimary Dependencies\n~~~~~~~~~~~~~~~~~~~~\n\n**Colour - HDRI** requires various dependencies in order to run:\n\n- `python >= 3.8, < 4 <https://www.python.org/download/releases/>`__\n- `colour-science <https://pypi.org/project/colour-science/>`__\n- `recordclass <https://pypi.org/project/recordclass/>`__\n\nOptional Features Dependencies\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n- `colour-demosaicing <https://pypi.org/project/colour-demosaicing/>`__\n- `Adobe DNG Converter <https://www.adobe.com/support/downloads/product.jsp?product=106&platform=Mac>`__\n- `dcraw <https://www.cybercom.net/~dcoffin/dcraw/>`__\n- `ExifTool <http://www.sno.phy.queensu.ca/~phil/exiftool/>`__\n- `rawpy <https://pypi.org/project/rawpy/>`__\n\nPypi\n~~~~\n\nOnce the dependencies are satisfied, **Colour - HDRI** can be installed from\nthe `Python Package Index <http://pypi.python.org/pypi/colour-hdri>`__ by\nissuing this command in a shell::\n\n    pip install --user colour-hdri\n\nThe optional features dependencies are installed as follows::\n\n    pip install --user 'colour-hdri[optional]'\n\nThe figures plotting dependencies are installed as follows::\n\n    pip install --user 'colour-hdri[plotting]'\n\nThe overall development dependencies are installed as follows::\n\n    pip install --user 'colour-hdri[development]'\n\nContributing\n^^^^^^^^^^^^\n\nIf you would like to contribute to `Colour - HDRI <https://github.com/colour-science/colour-hdri>`__,\nplease refer to the following `Contributing <https://www.colour-science.org/contributing/>`__\nguide for `Colour <https://github.com/colour-science/colour>`__.\n\nBibliography\n^^^^^^^^^^^^\n\nThe bibliography is available in the repository in\n`BibTeX <https://github.com/colour-science/colour-hdri/blob/develop/BIBLIOGRAPHY.bib>`__\nformat.\n\nAPI Reference\n-------------\n\nThe main technical reference for `Colour - HDRI <https://github.com/colour-science/colour-hdri>`__\nis the `API Reference <https://colour-hdri.readthedocs.io/en/latest/reference.html>`__.\n\nSee Also\n--------\n\nPublications\n^^^^^^^^^^^^\n\n- `Advanced High Dynamic Range Imaging: Theory and Practice <https://dl.acm.org/doi/book/10.5555/1996408>`__ by Banterle, F. et al.\n\n*Advanced High Dynamic Range Imaging: Theory and Practice* was used as a\nreference for some of the algorithms of **Colour - HDRI**.\n\nSoftware\n^^^^^^^^\n\n**C/C++**\n\n- `OpenCV <https://opencv.org/>`__ by Bradski, G.\n- `Piccante <https://github.com/cnr-isti-vclab/piccante>`__ by Banterle, F. and Benedetti, L.,\n\n*Piccante* was used to verify the Grossberg (2003) Histogram Based Image Sampling.\n\n**Matlab**\n\n- `HDR Toolbox <https://github.com/banterle/HDR_Toolbox>`__ by Banterle, F. et al.\n\nCode of Conduct\n---------------\n\nThe *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,\nis available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct/>`__ page.\n\nContact & Social\n----------------\n\nThe *Colour Developers* can be reached via different means:\n\n- `Email <mailto:colour-developers@colour-science.org>`__\n- `Discourse <https://colour-science.discourse.group/>`__\n- `Facebook <https://www.facebook.com/python.colour.science>`__\n- `Github Discussions <https://github.com/colour-science/colour-hdri/discussions>`__\n- `Gitter <https://gitter.im/colour-science/colour>`__\n- `Twitter <https://twitter.com/colour_science>`__\n\nAbout\n-----\n\n| **Colour - HDRI** by Colour Developers\n| Copyright 2015 Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__\n| This software is released under terms of New BSD License: https://opensource.org/licenses/BSD-3-Clause\n| `https://github.com/colour-science/colour-hdri <https://github.com/colour-science/colour-hdri>`__\n",
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
