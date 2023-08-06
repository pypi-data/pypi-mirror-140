# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pywgkey']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.5.0,<2.0.0', 'click>=8.0.4,<9.0.0']

setup_kwargs = {
    'name': 'pywgkey',
    'version': '1.0.0',
    'description': 'A simple WireGuard key generator writen in python.',
    'long_description': '[![CI](https://github.com/polluxtroy3758/pywgkey/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/polluxtroy3758/pywgkey/actions/workflows/ci.yml) [![CD](https://github.com/polluxtroy3758/pywgkey/actions/workflows/cd.yml/badge.svg)](https://github.com/polluxtroy3758/pywgkey/actions/workflows/cd.yml) [![codecov](https://codecov.io/gh/polluxtroy3758/pywgkey/branch/main/graph/badge.svg?token=Y6Y7A1DP0B)](https://codecov.io/gh/polluxtroy3758/pywgkey) ![PyPI](https://img.shields.io/pypi/v/pywgkey)\n\n# PyWgKey\n\nA simple WireGuard key generator writen in python.\n\n## Installation\n\n```\npip install pywgkey\n```\n\n## Usage\n\n```\n$ python -m pywgkey -h\nusage: python -m pywgkey [-h] [-b] [-w] [-p] string\n\nGenerate wg keypair containing specified string\n\npositional arguments:\n  string          The string that must be found in the pubkey\n\noptional arguments:\n  -h, --help      show this help message and exit\n  -b, --begining  If the pubkey must start with the string (default: False)\n  -w, --write     Write keys to files\n  -p, --psk       Genarate a preshared key as well\n```\n\n### Generate and print a keypair containing a string\n\n```\n$ python -m pywgkey test\nYour public key is:  1f810nNMhOB8mYpGbEvDwmXTeStPMycLiHpw0/CeL1c=\nYour private key is: 75C5ahPr5UY3paWXvLRKd82EK7KWuDDJ0D9h7/p21Us=\n```\n\n### Generate and write the keys to the current folder\n\n```\n$ python -m pywgkey test -w\nKeys have been writen to test.pub and test.priv\n$ cat test.pub\n1f810nNMhOB8mYpGbEvDwmXTeStPMycLiHpw0/CeL1c=\n$ cat test.priv\n75C5ahPr5UY3paWXvLRKd82EK7KWuDDJ0D9h7/p21Us=\n```\n\n### If you want the public key to **start** with a string (case is ignored)\n\n```\n$ python -m pywgkey test -b\nYour public key is:  TEsTtKLgqud0Yohg8geFKcnGy99xFzZlMvSv2YbwT1Y=\nYour private key is: paknyfh/d0LhZP2LqtjzJs2UE6XwaN14irxFdLV6d94=\n```\n',
    'author': 'polluxtroy3758',
    'author_email': '2147396+polluxtroy3758@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/polluxtroy3758/pywgkey',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
