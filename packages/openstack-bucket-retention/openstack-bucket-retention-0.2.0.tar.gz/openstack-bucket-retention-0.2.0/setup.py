# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openstack_bucket_retention']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'python-keystoneclient>=4.4.0,<5.0.0',
 'python-swiftclient>=3.13.0,<4.0.0']

entry_points = \
{'console_scripts': ['openstack-bucket-retention = '
                     'openstack_bucket_retention.cli:main']}

setup_kwargs = {
    'name': 'openstack-bucket-retention',
    'version': '0.2.0',
    'description': 'Openstack Bucket (Container) Retention',
    'long_description': '# openstack-bucket-retention [![PyPi version](https://img.shields.io/pypi/v/openstack-bucket-retention.svg)](https://pypi.python.org/pypi/openstack-bucket-retention/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/openstack-bucket-retention.svg)](https://pypi.python.org/pypi/openstack-bucket-retention/) [![](https://img.shields.io/github/license/f9n/openstack-bucket-retention.svg)](https://github.com/f9n/openstack-bucket-retention/blob/main/LICENSE)\n\nOpenstack bucket retention cli\n\n\n## Installation\n\n```\n$ # Install\n$ python3 -m pip install openstack-bucket-retention --user\n\n$ # Install with upgrade\n$ python3 -m pip install openstack-bucket-retention --user --upgrade\n```\n\n## Usage\n\nFirst you need to download \'OpenStack RC File\' on openstack provider. And Source the sh file.\n\n```bash\n$ openstack-bucket-retention --help\n\n$ # Show version\n$ openstack-bucket-retention version\nopenstack-bucket-retention: 0.1.0\n\n$ # Set Openstack environment variables\n$ #  or\n$ # Use \'OpenStack RC File\' on openstack provider. Download and Source the file.\n$ source Openstack-openrc.sh\n$ openstack-bucket-retention run --bucket-name "test-bucket" --retention-time "1w"\n\n```\n',
    'author': 'Fatih Sarhan',
    'author_email': 'f9n@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/f9n/openstack-bucket-retention',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
