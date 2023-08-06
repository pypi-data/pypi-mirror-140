# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anilist_man']

package_data = \
{'': ['*']}

install_requires = \
['platformdirs>=2.5.1,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['anilist-man = anilist_man.main:app']}

setup_kwargs = {
    'name': 'anilist-man',
    'version': '0.4.0',
    'description': 'A command-line-tool for AniList',
    'long_description': '# Anilist Man\n\n<p align="left">\n  <img src="https://repository-images.githubusercontent.com/463782270/36ac76f6-ad08-486a-94ff-b1b2a082f95b" alt="Banner" width="792">\n</p>\n\n`anilist-man` : python command-line tool for managing your data on [AniList](https://anilist.co) , made by [@ayushsehrawat](https://github.com/AyushSehrawat) in Typer.\n\n---\n\n## Contents\n\n * [Why?](#why)\n * [Installation](#installation)\n * [Usage](#usage)\n\n---\n\n## Why?\n\n`anilist-man` is a tool which can\n- Easily update progress in few steps\n- Remove the hassle of finding via search by chapter\n- Has custom name for better user friendly and easier to navigate\n\n---\n\n## Installation\n\n<p align="left">\n  <img src="https://github.com/minihut/anilist-man/raw/main/img/pip.png" alt="Pip" width="500">\n</p>\n\n\n## Usage\n\n<p align="left">\n  <img src="https://github.com/minihut/anilist-man/raw/main/img/usage.png" alt="CMD" width="500">\n</p>\n\n\n#### Todo\n\n- [x] Register on pypi ( python main.py -> some_command )\n- [ ] Fix `--` not in cli ( due to some issue not showing )\n- [ ] Add more support and commands \n- [ ] Fix saving of file issue\n\n#### Usage of code\nUsage of code for personal use ( editing , etc ) is allowed but user should give credits to this repository\n',
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
