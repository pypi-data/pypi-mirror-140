# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['materia', 'materia.spectra']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.1,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'unyt>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'materia-spectra',
    'version': '1.0.1',
    'description': 'Toolkit to analyze spectra.',
    'long_description': '======================\nMateria Spectra Module\n======================\n\n.. begin-description\n\n.. image:: https://codecov.io/gh/kijanac/materia-spectra/branch/main/graph/badge.svg?token=ESFSS6DIMR\n    :target: https://codecov.io/gh/kijanac/materia-spectra\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github\n\n**Toolkit for managing spectral data.**\n\nToolkit for managing spectral data through Materia.\n\n.. end-description\n\n---------------\nGetting Started\n---------------\n\nInstalling\n----------\n.. begin-installing\n\nFrom `pip <https://pypi.org/project/materia-spectra/>`_:\n\n``pip install materia-spectra``\n\nFrom `conda <https://anaconda.org/kijana/materia-spectra>`_:\n\n``conda install -c conda-forge -c kijana materia-spectra``\n\n.. end-installing\n\nDocumentation\n-------------\nSee documentation `here <https://kijanac.github.io/materia-spectra/>`_.\n\nExamples\n--------\nSee example scripts in `Examples <https://github.com/kijanac/materia-spectra/tree/main/examples>`_.\n\n.. begin-about\n\n-------\nAuthors\n-------\nKi-Jana Carter\n\n-------\nLicense\n-------\nThis project is licensed under the MIT License - see the `LICENSE <https://github.com/kijanac/materia-spectra/blob/main/LICENSE>`_ file for details.\n\n.. end-about\n\n.. begin-contributing\n\n------------\nContributing\n------------\nSee `CONTRIBUTING <https://github.com/kijanac/materia-spectra/blob/main/CONTRIBUTING.rst>`_.\n\n.. end-contributing\n',
    'author': 'Ki-Jana Carter',
    'author_email': 'kijana@mit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kijanac/materia-spectra',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
