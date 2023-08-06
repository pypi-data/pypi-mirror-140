# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rpgtk', 'rpgtk.cards']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rpgtk',
    'version': '0.2.1',
    'description': 'the python rpg toolkit',
    'long_description': "[![Coverage Status](https://coveralls.io/repos/github/is-gabs/rpgtk/badge.svg)](https://coveralls.io/github/is-gabs/rpgtk)\n\n# RPGTK \n\nRole-Playing Game Toolkit is a platform for build Python RPG's systems.\n\n## Installing\nInstall and update using [pip](https://pypi.org/project/rpgtk/):\n```\n$ pip install -U rpgtk\n```\n\n## A simple example\n```python\n# dice.py\nfrom rpgtk import Dice\n\ndice = Dice(sides=20)\n\ndice.roll()\n\nprint(dice)\n```\n```bash\npython dice.py\n'D20[6]'\n```\n\n```python\n# advantage roll\nfrom rpgtk import Dice\n\ndice = Dice(sides=20)\n\nadvantage_roll = max(dice * 2)\n\nprint(advantage_roll)\n```\n",
    'author': 'Gabriel Sarmento',
    'author_email': 'gabrielfs.bot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/is-gabs/rpgtk',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
