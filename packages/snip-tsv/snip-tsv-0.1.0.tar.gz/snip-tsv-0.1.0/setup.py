# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['snip_tsv']
install_requires = \
['matplotlib>=3.5.1,<4.0.0']

entry_points = \
{'console_scripts': ['snip = snip_tsv:main']}

setup_kwargs = {
    'name': 'snip-tsv',
    'version': '0.1.0',
    'description': 'Crop tabular data files',
    'long_description': '# snip-tsv\n',
    'author': 'Andrew Ross',
    'author_email': 'andrew.ross.mail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrewrosss/snip-tsv',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
