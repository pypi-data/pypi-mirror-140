# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['p3orm']

package_data = \
{'': ['*']}

install_requires = \
['PyPika>=0.48.8,<0.49.0', 'asyncpg>=0.24.0,<0.25.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'p3orm',
    'version': '0.3.3',
    'description': 'Python PyPika Postgres ORM',
    'long_description': '# p3orm\n\n<a href="https://rafalstapinski.github.io/p3orm">\n  <img src="https://rafalstapinski.github.io/p3orm/img/logo.svg" alt="p3orm logo" />\n</a>\n\n<p align="center">\n  <strong>\n    <em>\n      Utilitarian Python ORM for Postgres, backed by <a href="https://github.com/MagicStack/asyncpg">asyncpg</a>, <a href="https://github.com/samuelcolvin/pydantic">Pydantic</a>, and <a href="https://github.com/kayak/pypika">PyPika</a>\n    </em>\n  </strong>\n</p>\n\n<p align="center">\n  <a href="https://github.com/rafalstapinski/porm/actions/workflows/test.yml" target="_blank">\n    <img src="https://github.com/rafalstapinski/porm/actions/workflows/test.yml/badge.svg" alt="Test Status" />\n  </a>\n  <a href="https://pypi.org/project/p3orm" target="_blank">\n    <img src="https://img.shields.io/pypi/v/p3orm?color=%2334D058" alt="pypi" />\n  </a>\n  <a href="https://pypi.org/project/p3orm" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/p3orm?color=%23334D058" alt="Supported Python Versions: 3.8, 3.9, 3.10" />\n  </a>\n  <a href="https://github.com/rafalstapinski/p3orm/blob/master/LICENSE" target="_blank">\n    <img src="https://img.shields.io/pypi/l/p3orm?color=%23334D058" alt="MIT License" />\n  </a>\n</p>\n\n<h2>Philosophy</h2>\n\n90% of the time we talk to a database is with a CRUD operation. p3orm provides convenience helpers for fetching (one, first, many), inserting (one, many), updating (one), and deleting (one, many).\n\nThe remaining 10% is a bit more complicated. p3orm doesn\'t attempt to hide SQL queries or database interactions behind any magic. Instead, it empowers you to write direct and legible SQL queries with [PyPika](https://github.com/kayak/pypika) and execute them explicitly against the database.\n\n\n### Objects created or fetched by p3orm are dead, they\'re just [Pydantic](https://github.com/samuelcolvin/pydantic) models. If you want to interact with the database, you do so explicitly.\n\n<h2>Features</h2>\n\n- Comprehensive type annotations (full intellisense support)\n- Type validation\n- Full support for PyPika queries\n- Support for all `asyncpg` [types](https://magicstack.github.io/asyncpg/current/usage.html#type-conversion)\n\n<h2>Installation</h2>\n\nInstall with `poetry`\n```sh\npoetry add p3orm\n```\n\nor with `pip`\n\n```sh\npip install p3orm\n```\n\n<h2>Basic Usage</h2>\n\n```python\n\nfrom datetime import datetime\n\nfrom p3orm.core import Porm\nfrom p3orm.table import Table, PormField\n\nclass Thing(Table):\n    id = PormField(int, "id", pk=True, autogen=True)\n    name = PormField(str, "name")\n    created_at = PormField(datetime, "created_at", autogen=True)\n\nawait Porm.connect(user=..., password=..., database=..., host=..., port=...)\n\nthing = Thing(name="Name")\n\ninserted = await Thing.insert_one(thing)\n\nfetched = await Thing.fetch_first(Thing.id == 1)\n\nfetched.name = "Changed"\n\nupdated = await Thing.update_one(fetched)\n\ndeleted = await Thing.delete_where(Thing.id == updated.id)\n```\n\n<h2>Usage</h2>\n\nSee <a href="https://rafalstapinski.github.io/p3orm">docs</a>\n',
    'author': 'Rafal Stapinski',
    'author_email': 'stapinskirafal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rafalstapinski.github.io/p3orm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
