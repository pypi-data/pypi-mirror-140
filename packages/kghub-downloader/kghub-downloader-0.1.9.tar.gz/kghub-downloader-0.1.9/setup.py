# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kghub_downloader']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>5.0,<7.0',
 'compress-json>1.0,<2.0',
 'elasticsearch',
 'google-cloud-storage>=2.1.0,<3.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'typer==0.4']

entry_points = \
{'console_scripts': ['downloader = kghub_downloader.main:typer_app']}

setup_kwargs = {
    'name': 'kghub-downloader',
    'version': '0.1.9',
    'description': 'Downloads and caches files for knowledge graph ETL',
    'long_description': None,
    'author': 'The Monarch Initiative',
    'author_email': 'info@monarchinitiative.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
