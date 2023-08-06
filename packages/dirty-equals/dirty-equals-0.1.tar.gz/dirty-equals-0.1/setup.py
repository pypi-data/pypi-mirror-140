# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dirty_equals']

package_data = \
{'': ['*']}

install_requires = \
['pytz>=2021.3,<2022.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.0.1,<5.0.0']}

setup_kwargs = {
    'name': 'dirty-equals',
    'version': '0.1',
    'description': 'Doing dirty (but extremely useful) things with equals.',
    'long_description': '<p align="center">\n  <a href="https://dirty-equals.helpmanual.io">\n    <img src="https://dirty-equals.helpmanual.io/img/logo-text.svg" alt="dirty-equals">\n  </a>\n</p>\n<p align="center">\n  <em>Doing dirty (but extremely useful) things with equals.</em>\n</p>\n<p align="center">\n  <a href="https://github.com/samuelcolvin/dirty-equals/actions?query=event%3Apush+branch%3Amain+workflow%3ACI">\n    <img src="https://github.com/samuelcolvin/dirty-equals/workflows/CI/badge.svg?event=push" alt="CI">\n  </a>\n  <a href="https://codecov.io/gh/samuelcolvin/dirty-equals">\n    <img src="https://codecov.io/gh/samuelcolvin/dirty-equals/branch/main/graph/badge.svg" alt="Coverage">\n  </a>\n  <a href="https://pypi.python.org/pypi/dirty-equals">\n    <img src="https://img.shields.io/pypi/v/dirty-equals.svg" alt="pypi">\n  </a>\n  <a href="https://github.com/samuelcolvin/dirty-equals">\n    <img src="https://img.shields.io/pypi/pyversions/dirty-equals.svg" alt="versions">\n  </a>\n  <a href="https://github.com/samuelcolvin/dirty-equals/blob/main/LICENSE">\n    <img src="https://img.shields.io/github/license/samuelcolvin/dirty-equals.svg" alt="license">\n  </a>\n</p>\n\n---\n\n**Documentation**: [dirty-equals.helpmanual.io](https://dirty-equals.helpmanual.io)\n\n**Source Code**: [github.com/samuelcolvin/dirty-equals](https://github.com/samuelcolvin/dirty-equals)\n\n---\n\n**dirty-equals** is a python library that (mis)uses the `__eq__` method to make python code (generally unit tests)\nmore declarative and therefore easier to read and write.\n\n*dirty-equals* can be used in whatever context you like, but it comes into its own when writing unit tests for\napplications where you\'re commonly checking the response to API calls and the contents of a database.\n\n## Usage\n\nHere\'s a trivial example of what *dirty-equals* can do:\n\n```py\nfrom dirty_equals import IsPositive\n\nassert 1 == IsPositive\nassert -2 == IsPositive  # this will fail!\n```\n\n**That doesn\'t look very useful yet!**, but consider the following unit test code using *dirty-equals*:\n\n```py title="More Powerful Usage"\nfrom dirty_equals import IsJson, IsNow, IsPositiveInt, IsStr\n\n...\n\n# user_data is a dict returned from a database or API which we want to test\nassert user_data == {\n    # we want to check that id is a positive int\n    \'id\': IsPositiveInt,\n    # we know avatar_file should be a string, but we need a regex as we don\'t know whole value\n    \'avatar_file\': IsStr(regex=r\'/[a-z0-9\\-]{10}/example\\.png\'),\n    # settings_json is JSON, but it\'s more robust to compare the value it encodes, not strings\n    \'settings_json\': IsJson({\'theme\': \'dark\', \'language\': \'en\'}),\n    # created_ts is datetime, we don\'t know the exact value, but we know it should be close to now\n    \'created_ts\': IsNow(delta=3),\n}\n```\n\nWithout *dirty-equals*, you\'d have to compare individual fields and/or modify some fields before comparison -\nthe test would not be declarative or as clear.\n\n*dirty-equals* can do so much more than that, for example:\n\n* [`IsPartialDict`](https://dirty-equals.helpmanual.io/types/#dirty_equals.IsPartialDict) \n  let\'s you compare a subset of a dictionary\n* [`IsStrictDict`](https://dirty-equals.helpmanual.io/types/#dirty_equals.IsStrictDict) \n  let\'s you confirm order in a dictionary\n* [`IsList`](https://dirty-equals.helpmanual.io/types/#dirty_equals.IsList) and \n  [`IsTuple`](https://dirty-equals.helpmanual.io/types/#dirty_equals.IsTuple)\n  lets you compare partial lists and tuples, with or without order constraints\n* nesting any of these types inside any others\n* [`IsInstance`](https://dirty-equals.helpmanual.io/types/#dirty_equals.IsInstance) \n  lets you simply confirm the type of an object\n* You can even use boolean operators `|` and `&` to combine multiple conditions\n* and much more...\n\n## Installation\n\nSimply:\n\n```bash\npip install dirty-equals\n```\n\n**dirty-equals** requires **Python 3.7+**.\n',
    'author': 'Samuel Colvin',
    'author_email': 's@muelcolvin.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://dirty-equals.helpmanual.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
