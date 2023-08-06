# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyxstar']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.5.0,<5.0.0']

entry_points = \
{'console_scripts': ['pyxstar = pyxstar.main:main']}

setup_kwargs = {
    'name': 'pyxstar',
    'version': '0.1.1',
    'description': 'A library and commandline tool for managing Pix-Star digital photo frames',
    'long_description': "A Python library and commandline tool for managing [Pix-Star](https://www.pix-star.com/) digital photo frames.\n\n# Installation\n\nYou can install from PyPI using `pip` as follows\n\n```bash\npip install pyxstar\n```\n\n# Usage\n\n## Python library\n\nThe `pyxstar.api` module is the basis for all API interactions with the Pix-Star service. The `API` class should be used to invoke methods on the service, which accept and return `Album` and `Photo` classes.\n\nFor example\n\n```python\nfrom pyxstar.api import API\n\napi = API()\napi.login('myusername', 'mypassword')\nfor a in api.albums():\n    print(f'Album: {a.name}')\n\n    for p in api.album_photos(a):\n        print(f'  Photo: {p.name}')\n```\n\n## Commandline\n\nThis package provides a `pyxstar` commandline tool which offers a variety of subcommands to interact with your digital photo frame.\n\nThe following are some examples of how to use this:\n\n```bash\n# Show help\n$ pyxstar help\n[...]\n\n# List album names\n$ pyxstar -u myusername -p mypassword ls\nMy First Album\nMy Second Album\n\n# List photos in My First Album\n$ pyxstar -u myusername -p mypassword ls 'My First Album'\n315371094   _dsc1254_59.jpg\n315371095   _dsc1254_60.jpg\n\n# Upload a photo to My First Album and check that it exists\n$ pyxstar -u myusername -p mypassword upload 'My First Album' /path/to/foo.jpg\n$ pyxstar -u myusername -p mypassword ls 'My First Album'\n315371094   _dsc1254_59.jpg\n315371095   _dsc1254_60.jpg\n315371099   foo.jpg\n```\n",
    'author': 'Peter Griess',
    'author_email': 'pg@std.in',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pgriess/pyxstar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
