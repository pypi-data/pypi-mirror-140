# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['theseptatimes']

package_data = \
{'': ['*']}

install_requires = \
['DateTime>=4.4,<5.0',
 'argparse>=1.4.0,<2.0.0',
 'colorama>=0.4.4,<0.5.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'requests>=2.27.1,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['tst = theseptatimes.cli:main']}

setup_kwargs = {
    'name': 'theseptatimes',
    'version': '0.1.0',
    'description': 'A Python package to get data from the Septa API',
    'long_description': '<h2 align="center"> ━━━━━━  ❖  ━━━━━━ </h2>\n\n<!-- BADGES -->\n<div align="center">\n   <p></p>\n   \n   <img src="https://img.shields.io/github/stars/zenithds/TheSeptaTimes?color=F8BD96&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/forks/zenithds/TheSeptaTimes?color=DDB6F2&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/repo-size/zenithds/TheSeptaTimes?color=ABE9B3&labelColor=302D41&style=for-the-badge">\n   \n   <img src="https://badges.pufler.dev/visits/zenithds/TheSeptaTimes?style=for-the-badge&color=96CDFB&logoColor=white&labelColor=302D41"/>\n   <br>\n</div>\n\n<p/>\n\n---\n\n### ❖ TheSeptaTimes\n\nTheSeptaTimes is a python package designed to make accessing info about Septa\'s regional rail network easier. I made this because I commute to college every day via septa, and checking the time for the next train via the app or the website simply takes too much time. I wanted something I could access from my terminal, and thus, TheSeptaTimes was born. \n\n  <img src="assets/septa.gif" alt="septa gif">\n\n---\n\n### ❖ Installation\n\n> Install from pip\n\n```sh\n$ pip3 install TheSeptaTimes\n```\n\n> Install from source\n- First, install [poetry](https://python-poetry.org/)\n\n```sh\n$ git clone https://github.com/ZenithDS/TheSeptaTimes.git\n$ cd TheSeptaTimes\n$ poetry build\n$ pip3 install ./dist/theseptatimes-0.0.11.tar.gz\n```\n\n---\n\n### ❖ Usage\n\n<details>\n<summary><strong>As CLI App</strong></summary>\n\n```sh\nusage: tst [-h] [-o ORIGIN] [-d DESTINATION] [-s STATION] [-t TRAINID] [-n NUMRESULTS] action\n\npositional arguments:\n  action                Determines whether you want to `search` or `list`\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o ORIGIN, --origin ORIGIN\n                        the starting train station\n  -d DESTINATION, --destination DESTINATION\n                        the ending station\n  -s STATION, --station STATION\n                        any given station\n  -t TRAINID, --trainID TRAINID\n                        the ID of any given train\n  -n NUMRESULTS, --numResults NUMRESULTS\n                        the number of results\n```\n\n> Search for a train station\n```sh\n$ tst search admr\n  \n  Station matching your guess: Ardmore\n ```\n\n> Get times for the next two trains that go from a given train station to another\n```sh\n$ tst next \'30th Street Station\' \'North Philadelphia\'\n```\n\n> List the next 6 arrivals at a given train station\n```sh\n$ tst arrivals \'30th Street Station\' 6\n```\n\n> Take a look at any given train\'s schedule using the train number\n```sh\n$ tst train 9374\n```\n\n</details>\n\n<details>\n<summary><strong>As Python Library/Package</strong></summary>\n\n> print the next train going from a given train station to another\n```python\nfrom TheSeptaTimes.SeptaTimes import TheSeptaTimes\n\nsepta = TheSeptaTimes()\n\nnext_trains = septa.get_next_to_arrive(\'30th Street Station\', \'North Philadelphia\', 1)\nreadable_next_trains = septa.parse_next_to_arrive(next_trains)\n\nfor train in readable_next_trains:\n    print(train)\n```\n\n> print the next 6 arrivals at a given train station\n```python\nfrom TheSeptaTimes.SeptaTimes import TheSeptaTimes\n\nsepta = TheSeptaTimes()\n\ntrains = septa.get_station_arrivals(\'30th Street Station\', 5)\nreadable_trains = septa.parse_station_arrivals(trains)\n\nfor train in readable_trains:\n    print(trains)\n```\n\n> print any given train\'s schedule using the train number\n```python\nfrom TheSeptaTimes.SeptaTimes import TheSeptaTimes\n\nsepta = TheSeptaTimes()\n\ntrain_schedule = septa.get_train_schedule(9374)\nreadable_train_schedule = septa.parse_train_schedule(train_schedule)\n\nfor stop in readable_train_schedule:\n    print(stop)\n    \n ```\n\n</details>\n\n---\n\n### ❖ What\'s New? \n0.1.00 - an overhaul to the cli interface\n\n---\n\n<div align="center">\n\n   <img src="https://img.shields.io/static/v1.svg?label=License&message=MIT&color=F5E0DC&labelColor=302D41&style=for-the-badge">\n\n</div>\n\n',
    'author': 'ZenithDS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
