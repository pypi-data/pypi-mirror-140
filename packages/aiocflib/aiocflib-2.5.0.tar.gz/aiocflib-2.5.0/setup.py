# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aiocflib',
 'aiocflib.benchmarks',
 'aiocflib.bootloader',
 'aiocflib.crazyflie',
 'aiocflib.crtp',
 'aiocflib.crtp.drivers',
 'aiocflib.crtp.middleware',
 'aiocflib.drivers',
 'aiocflib.utils']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.2.1,<4.0.0',
 'colorama>=0.4.3,<0.5.0',
 'colour>=0.1.5,<0.2.0',
 'hexdump>=3.3,<4.0',
 'outcome>=1.0.1,<2.0.0',
 'pyusb>=1.0.2,<2.0.0']

setup_kwargs = {
    'name': 'aiocflib',
    'version': '2.5.0',
    'description': 'Python async API for Crazyflie drones',
    'long_description': None,
    'author': 'Tamas Nepusz',
    'author_email': 'tamas@collmot.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
