# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anilist_man']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['anilist-man = anilist_man.main:app']}

setup_kwargs = {
    'name': 'anilist-man',
    'version': '0.2.8a0',
    'description': '',
    'long_description': '# Anilist-Man\nA python command-line tool for [AniList](https://anilist.co) , made by [@ayushsehrawat](https://github.com/AyushSehrawat) in Typer.\n\n---\n\n## Setup/Installation\n\nSoon\n\n---\n\n#### Todo\n\n- [ ] Add more support and commands \n- [ ] Register on pypi ( python main.py -> some_command )\n\n#### Using of Code\nIf you want to use this code , you can use it in your project but you must give credit to this repo.',
    'author': 'Mini',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minihut/anilist-man',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
