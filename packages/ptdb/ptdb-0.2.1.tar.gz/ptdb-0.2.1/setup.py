# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ptdb']

package_data = \
{'': ['*']}

install_requires = \
['ptpython>=3.0.20,<4.0.0']

setup_kwargs = {
    'name': 'ptdb',
    'version': '0.2.1',
    'description': 'A pdb class based on ptpython',
    'long_description': '# ptb\n\n![Usage](https://raw.githubusercontent.com/4thel00z/ptdb/master/ptdb.png)\n\n## Motivation\n\npdb sucks, the other packages do weird stuff and type completion does not work in interact mode (looking at you ipdb).\n\n## Installation\n\n```\npip install ptb\n```\n\n## Usage\n\nSimple do:\n\n```python3\nfrom ptdb import set_trace\n\n# some where in your code do:\n\nset_trace()\n\n# Then just type the following to be thrown into a ptpython shell\ninteract\n```\n\n\n## License\n\nThis project is licensed under the GPL-3 license.\n',
    'author': '4thel00z',
    'author_email': '4thel00z@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/4thel00z/ptdb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
