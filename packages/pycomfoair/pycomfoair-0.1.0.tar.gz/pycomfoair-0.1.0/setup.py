# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['comfoair']

package_data = \
{'': ['*']}

install_requires = \
['async-timeout>=4.0.2,<5.0.0',
 'bitstring>=3.1.9,<4.0.0',
 'pyserial-asyncio>=0.6,<0.7']

setup_kwargs = {
    'name': 'pycomfoair',
    'version': '0.1.0',
    'description': 'Interface for Zehnder ComfoAir 350 ventilation units',
    'long_description': '# pycomfoair\nPython library to monitor and control Zehnder ComfoAir 350 units\n',
    'author': 'Andreas Oberritter',
    'author_email': 'obi@saftware.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mtdcr/pycomfoair',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
