# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['businessready']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2==2.11.2', 'MarkupSafe==2.0.1', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['wikimd = brd.script:run']}

setup_kwargs = {
    'name': 'businessready',
    'version': '0.7.47',
    'description': 'Transform Cisco CLIs and APIs into Business Ready Documents',
    'long_description': None,
    'author': 'John Capobianco',
    'author_email': 'ptcapo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
