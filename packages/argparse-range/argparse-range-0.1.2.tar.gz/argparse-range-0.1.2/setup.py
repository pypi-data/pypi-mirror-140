# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['argparse_range']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'argparse-range',
    'version': '0.1.2',
    'description': 'Numeric range for argparse arguments',
    'long_description': '<div align="center">\n\n[![pypi](https://img.shields.io/pypi/v/argparse-range)](https://pypi.org/project/argparse-range/)\n[![github](https://img.shields.io/static/v1?label=&message=github&color=grey&logo=github)](https://github.com/aatifsyed/argparse-range)\n\n</div>\n\n# `argparse-range`\nEasily check that an argument is within a range for argparse\n\nUse it like this:\n```python\n>>> from argparse import ArgumentParser, ArgumentTypeError\n>>> from argparse_range import range_action\n>>> parser = ArgumentParser()\n>>> _ = parser.add_argument("rangedarg", action=range_action(0, 10), help="An argument")\n>>> args = parser.parse_args(["0"])\n>>> args.rangedarg\n0\n>>> parser.parse_args(["20"])\nTraceback (most recent call last):\n    ....\nargparse.ArgumentTypeError: Invalid choice: 20 (must be in range 0..=10)\n\n```\n\n## Features\n### Helptext is added transparently\n```text\nfoo.py --help\n\nusage: foo.py [-h] rangedarg\n\npositional arguments:\n  rangedarg   An argument (must be in range 0..=10)\n\noptional arguments:\n  -h, --help  show this help message and exit\n```\n\n### Infers type by default\n```python\n>>> from argparse import ArgumentParser\n>>> from argparse_range import range_action\n>>> parser = ArgumentParser()\n>>> _ = parser.add_argument("intarg", action=range_action(0, 10))\n>>> _ = parser.add_argument("floatarg", action=range_action(25.0, 40.0))\n>>> _ = parser.add_argument("explicit", action=range_action(25.0, 40.0), type=int)\n>>> args = parser.parse_args(["5", "30", "30"])\n>>> assert isinstance(args.intarg, int)\n>>> assert isinstance(args.floatarg, float)\n>>> assert isinstance(args.explicit, int)\n\n```\n\n### Handles optional arguments and defaults just like normal parsing\n```python\n>>> from argparse import ArgumentParser\n>>> from argparse_range import range_action\n>>> parser = ArgumentParser()\n>>> _ = parser.add_argument("--maybe", action=range_action(0, 10), nargs="?")\n>>> parser.parse_args([])\nNamespace(maybe=None)\n>>> parser.parse_args(["--maybe"])\nNamespace(maybe=None)\n>>> parser.parse_args(["--maybe", "5"])\nNamespace(maybe=5)\n>>> parser.parse_args(["--maybe", "20"])\nTraceback (most recent call last):\n    ....\nargparse.ArgumentTypeError: Invalid choice: 20 (must be in range 0..=10)\n\n```\n\n### Handles multiple arguments just like normal parsing\n```python\n>>> from argparse import ArgumentParser\n>>> from argparse_range import range_action\n>>> parser = ArgumentParser()\n>>> _ = parser.add_argument("many", action=range_action(0, 10), nargs="*")\n>>> parser.parse_args([])\nNamespace(many=[])\n>>> parser.parse_args(["5"])\nNamespace(many=[5])\n>>> parser.parse_args(["1", "2", "3", "4"])\nNamespace(many=[1, 2, 3, 4])\n\n```\n',
    'author': 'Aatif Syed',
    'author_email': 'aatifsyedyp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aatifsyed/argparse-range',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
