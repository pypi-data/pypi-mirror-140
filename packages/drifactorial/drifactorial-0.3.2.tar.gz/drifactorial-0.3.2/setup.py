# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drifactorial']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.6.3,<5.0.0']}

setup_kwargs = {
    'name': 'drifactorial',
    'version': '0.3.2',
    'description': 'Python client for the Factorial API.',
    'long_description': '<p style="text-align: center; padding-bottom: 1rem;">\n    <a href="https://dribia.github.io/drifactorial">\n        <img \n            src="https://dribia.github.io/drifactorial/img/logo_dribia_blau_cropped.png" \n            alt="drifactorial" \n            style="display: block; margin-left: auto; margin-right: auto; width: 40%;"\n        >\n    </a>\n</p>\n\n<p style="text-align: center">\n    <a href="https://github.com/dribia/drifactorial/actions?query=workflow%3ATest" target="_blank">\n    <img src="https://github.com/dribia/drifactorial/workflows/Test/badge.svg" alt="Test">\n    </a>\n    <a href="https://github.com/dribia/drifactorial/actions?query=workflow%3APublish" target="_blank">\n        <img src="https://github.com/dribia/drifactorial/workflows/Publish/badge.svg" alt="Publish">\n    </a>\n    <a href="https://codecov.io/gh/dribia/drifactorial" target="_blank">\n        <img src="https://img.shields.io/codecov/c/github/dribia/drifactorial?color=%2334D058" alt="Coverage">\n    </a>\n    <a href="https://pypi.org/project/drifactorial" target="_blank">\n        <img src="https://img.shields.io/pypi/v/drifactorial?color=%2334D058&label=pypi%20package" alt="Package version">\n    </a>\n</p>\n\n<p style="text-align: center;">\n    <em>Python client for the Factorial API.</em>\n</p>\n\n\n\n---\n\n**Documentation**: <a href="https://dribia.github.io/drifactorial" target="_blank">https://dribia.github.io/drifactorial</a>\n\n**Source Code**: <a href="https://github.com/dribia/drifactorial" target="_blank">https://github.com/dribia/drifactorial</a>\n\n---\n\n[Factorial](https://factorialhr.com/) is a software dedicated to manage everything related to HR.\n\n**Drifactorial** provides a tiny Python interface to the official API.\n\n## Key features\n\n* **Authorize programatic access** to your application.\n* Obtain and refresh **access tokens**.\n* Implements **generic GET and POST** methods.\n* Parses responses to **Pydantic models**.\n* Easily implement **additional methods**.\n\n## Example\n\nThe simplest example.\n\n```python\nfrom drifactorial import Factorial\nfrom datetime import datetime\n\nfactorial = Factorial(access_token="abc")\n\n# get list of employees\nemployees = factorial.get_employees()\n# get list of company holidays\nholidays = factorial.get_holidays()\n# get list of leaves\nleaves = factorial.get_leaves()\n# get list of days off of an employee\ndaysoff = factorial.get_daysoff(employee_id=123)\n# get list of all shifts in October 2021\nshifts = factorial.get_shifts(year=2021, month=10)\n# get single employee\nsingle_employee = factorial.get_single_employee(employee_id=123)\n# get my account\naccount = factorial.get_account()\n\n# clock in shift\nclock_in = datetime(2021, 10, 1, 9, 0)\nnew_shift = factorial.clock_in(now=clock_in, employee_id=123)\n# clock out shift\nclock_out = datetime(2021, 10, 1, 13, 0)\nupdated_shift = factorial.clock_out(now=clock_in, employee_id=123)\n```\n',
    'author': 'Dribia Data Research',
    'author_email': 'opensource@dribia.com',
    'maintainer': 'Xavier Hoffmann',
    'maintainer_email': 'xrhoffmann@gmail.com',
    'url': 'https://dribia.github.io/drifactorial',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
