# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobungie', 'aiobungie.crate', 'aiobungie.interfaces', 'aiobungie.internal']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.8.1', 'attrs==21.4.0', 'python-dateutil==2.8.2']

setup_kwargs = {
    'name': 'aiobungie',
    'version': '0.2.6a0',
    'description': 'A Python and Asyncio API for Bungie.',
    'long_description': '<div align="center">\n    <h1>aiobungie</h1>\n    <p>An asynchronous statically typed API wrapper for the Bungie API written in Python.</p>\n    <a href="https://codeclimate.com/github/nxtlo/aiobungie/maintainability">\n    <img src="https://api.codeclimate.com/v1/badges/09e71a0374875d4594f4/maintainability"/>\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/issues">\n    <img src="https://img.shields.io/github/issues/nxtlo/aiobungie"/>\n    </a>\n    <a href="http://python.org">\n    <img src="https://img.shields.io/badge/python-3.9%20%7C%203.10-blue"/>\n    </a>\n    <a href="https://pypi.org/project/aiobungie/">\n    <img src="https://img.shields.io/pypi/v/aiobungie?color=green"/>\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/blob/master/LICENSE">\n    <img src="https://img.shields.io/pypi/l/aiobungie"/>\n    </a>\n    <a href="https://github.com/nxtlo/aiobungie/actions/workflows/ci.yml">\n    <img src="https://github.com/nxtlo/aiobungie/actions/workflows/ci.yml/badge.svg?branch=master">\n    </a>\n</div>\n\n# Installing\n\nPyPI stable release.\n\n```sh\n$ pip install aiobungie\n```\n\nDevelopment\n```sh\n$ pip install git+https://github.com/nxtlo/aiobungie@master\n```\n\n## Quick Example\n\nSee [Examples for advance usage.](https://github.com/nxtlo/aiobungie/tree/master/examples)\n\n```python\nimport aiobungie\n\nclient = aiobungie.Client(\'YOUR_API_KEY\')\n\nasync def main() -> None:\n\n    # fetch a clan\n    clan = await client.fetch_clan("Nuanceㅤ")\n\n    for member in await clan.fetch_members():\n        if member.unique_name == "Fate怒#4275":\n\n            # Get the profile for this clan member.\n            profile = await member.fetch_self_profile(aiobungie.ComponentType.CHARACTERS)\n\n            # Get the character component for the profile.\n            if characters := profile.characters:\n                for character in characters.values():\n                    print(character.class_type, character.light, character.gender)\n\n                # Check some character stats.\n                for stat, stat_value in character.stats.items():\n                    if stat is aiobungie.Stat.MOBILITY and stat_value > 90:\n                        print(f"Zooming {stat_value} ⭐")\n\n# You can either run it using the client or just `asyncio.run(main())`\nclient.run(main())\n```\n\n## RESTful client\nAlternatively, You can use `RESTClient` which\'s designed to only make HTTP requests and return JSON objects.\n\n### Quick Example\n```py\nimport aiobungie\nimport asyncio\n\nasync def main(access_token: str) -> None:\n    async with aiobungie.RESTClient("TOKEN") as rest_client:\n        response = await rest_client.fetch_clan_members(4389205)\n        raw_members_payload = response[\'results\']\n\n        for member in raw_members_payload:\n            for k, v in member[\'destinyUserInfo\'].items():\n                print(k, v)\n\n            # aiobungie also exposes a method which lets you make your own requests.\n            await rest.static_request("POST", "Some/Endpoint", auth=access_token, json={...: ...})\n\n            # Methods only exposed through the rest client.\n            await rest.refresh_access_token(\'a token\')\n\nasyncio.run(main("DB_ACCESS_TOKEN"))\n```\n\n### Requirements\n* Python 3.9 or higher\n* aiohttp\n* attrs\n\n## Contributing\nPlease read this [manual](https://github.com/nxtlo/aiobungie/blob/master/CONTRIBUTING.md)\n\n### Getting Help\n* Discord: `Fate 怒#0008` | `350750086357057537`\n* Docs: [Here](https://nxtlo.github.io/aiobungie/).\n',
    'author': 'nxtlo',
    'author_email': 'dhmony-99@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nxtlo/aiobungie',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
