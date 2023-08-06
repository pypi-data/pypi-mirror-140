# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywgkey']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'pywgkey',
    'version': '0.2.2',
    'description': 'A simple WireGuard key generator writen in python.',
    'long_description': '![GitHub Workflow Status](https://img.shields.io/github/workflow/status/polluxtroy3758/pywgkey/Test?style=flat-square) ![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/polluxtroy3758/pywgkey?include_prereleases&style=flat-square)\n\n# PyWgKey\n\nA simple WireGuard key generator writen in python.\n\n## Installation\n\n```\npip install pywgkey\n```\n\n## Usage\n\n```\n$ python -m pywgkey -h\nusage: python -m pywgkey [-h] [-b] [-w] [-p] string\n\nGenerate wg keypair containing specified string\n\npositional arguments:\n  string          The string that must be found in the pubkey\n\noptional arguments:\n  -h, --help      show this help message and exit\n  -b, --begining  If the pubkey must start with the string (default: False)\n  -w, --write     Write keys to files\n  -p, --psk       Genarate a preshared key as well\n```\n\n### Generate and print a keypair containing a string\n\n```\n$ python -m pywgkey test\nYour public key is:  1f810nNMhOB8mYpGbEvDwmXTeStPMycLiHpw0/CeL1c=\nYour private key is: 75C5ahPr5UY3paWXvLRKd82EK7KWuDDJ0D9h7/p21Us=\n```\n\n### Generate and write the keys to the current folder\n\n```\n$ python -m pywgkey test -w\nKeys have been writen to test.pub and test.priv\n$ cat test.pub\n1f810nNMhOB8mYpGbEvDwmXTeStPMycLiHpw0/CeL1c=\n$ cat test.priv\n75C5ahPr5UY3paWXvLRKd82EK7KWuDDJ0D9h7/p21Us=\n```\n\n### If you want the public key to **start** with a string (case is ignored)\n\n```\n$ python -m pywgkey test -b\nYour public key is:  TEsTtKLgqud0Yohg8geFKcnGy99xFzZlMvSv2YbwT1Y=\nYour private key is: paknyfh/d0LhZP2LqtjzJs2UE6XwaN14irxFdLV6d94=\n```\n',
    'author': 'polluxtroy3758',
    'author_email': '2147396+polluxtroy3758@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/polluxtroy3758/pywgkey',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
