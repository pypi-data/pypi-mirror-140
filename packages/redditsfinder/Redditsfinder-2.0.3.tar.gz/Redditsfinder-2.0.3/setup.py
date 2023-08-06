# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redditsfinder']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'rich']

entry_points = \
{'console_scripts': ['redditsfinder = redditsfinder:main']}

setup_kwargs = {
    'name': 'redditsfinder',
    'version': '2.0.3',
    'description': "Archive a reddit user's post history. Formatted overview of a profile, JSON containing every post, and picture downloads.",
    'long_description': '# redditsfinder - reddit user info\n**`pip3 install redditsfinder`**\n\n**A program to get reddit user post data.**\n\n```Running redditsfinder\n\nTest it on a user to make sure it works.\n    redditsfinder someusername\n\nBasic usage\n    redditsfinder username\n    redditsfinder [options] username_0 username_1 username_2 ...\n\nWith an input file\n    -f or --file.\n    redditsfinder [options] -f line_separated_text_file.txt\n\nExamples\n    - just print the summary table to stdout\n        $ redditsfinder someusername\n\n    - save data locally and print the summary table to stdout\n        $ redditsfinder --write someusername\n\n    - just save data locally without printing\n        $ redditsfinder --write --quiet someusername\n\n    - download pictures\n        $ redditsfinder --pics someusername\n\nOptional args\n    --pics returns URLs of image uploads\n    -pics -d or --pics --download downloads them\n    -quiet or -q turns off printing\n```\n',
    'author': 'fitzy1293',
    'author_email': 'berkshiremind@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Fitzy1293/redditsfinder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
