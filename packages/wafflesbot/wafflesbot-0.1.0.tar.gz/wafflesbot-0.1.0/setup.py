# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wafflesbot']

package_data = \
{'': ['*']}

install_requires = \
['jmapc>=0.1.5,<0.2.0', 'replyowl>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['wafflesbot = wafflesbot.main:main']}

setup_kwargs = {
    'name': 'wafflesbot',
    'version': '0.1.0',
    'description': 'Tech recruiter auto reply bot using JMAP',
    'long_description': '# wafflesbot: Email auto reply bot for [JMAP][jmap] mailboxes\n\n[![PyPI](https://img.shields.io/pypi/v/wafflesbot)][pypi]\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wafflesbot)][pypi]\n[![Build](https://img.shields.io/github/checks-status/smkent/waffles/master?label=build)][gh-actions]\n[![codecov](https://codecov.io/gh/smkent/waffles/branch/master/graph/badge.svg)][codecov]\n[![GitHub stars](https://img.shields.io/github/stars/smkent/waffles?style=social)][repo]\n\n[![wafflesbot][logo]](#)\n\nwafflesbot sends form replies to unreplied emails in a [JMAP][jmap] mailbox\n(such as [Fastmail][fastmail]).\n\nwafflesbot excels at automatically asking tech recruiters for compensation\ninformation.\n\nBuilt on:\n* JMAP client: [jmapc][jmapc]\n* Quoted email reply assembly: [replyowl][replyowl]\n\n## Installation\n\n[wafflesbot is available on PyPI][pypi]:\n\n```\npip install wafflesbot\n```\n\n## Usage\n\nwafflesbot provides the `waffles` command which can be run interactively or as a\ncronjob.\n\nEnvironment variables:\n* `JMAP_HOST`: JMAP server hostname\n* `JMAP_USER`: Email account username\n* `JMAP_PASSWORD`: Email account password (likely an app password if 2-factor\n  authentication is enabled with your provider)\n\nRequired arguments:\n* `-m/--mailbox`: Name of the folder to process\n* `-r/--reply-content`: Path to file with an HTML reply message\n\n### Invocation examples\n\nReply to messages in the "Recruiters" folder with the message in `my-reply.html`:\n```py\nJMAP_HOST=jmap.example.com \\\nJMAP_USER=ness \\\nJMAP_PASSWORD=pk_fire \\\nwaffles \\\n    --mailbox "Recruiters" \\\n    --reply-content my-reply.html\n```\n\nAdditional argument examples:\n\n* Only reply to messages received within the last day:\n  * `waffles -m "Recruiters" -r my-reply.html --days 1` (or `-n`)\n* Send at most 2 emails before exiting:\n  * `waffles -m "Recruiters" -r my-reply.html --limit 2` (or `-l`)\n* Instead of sending mail, print constructed email replies to standard output:\n  * `waffles -m "Recruiters" -r my-reply.html --dry-run` (or `-p`)\n* Log JMAP requests and responses to the debug logger:\n  * `waffles -m "Recruiters" -r my-reply.html --debug` (or `-d`)\n\n## Development\n\nPrerequisites: [Poetry][poetry]\n\n* Setup: `poetry install`\n* Run all tests: `poetry run poe test`\n* Fix linting errors: `poetry run poe lint`\n\n---\n\nCreated from [smkent/cookie-python][cookie-python] using\n[cookiecutter][cookiecutter]\n\n[codecov]: https://codecov.io/gh/smkent/waffles\n[cookie-python]: https://github.com/smkent/cookie-python\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[fastmail]: https://fastmail.com\n[gh-actions]: https://github.com/smkent/waffles/actions?query=branch%3Amaster\n[jmap]: https://jmap.io\n[jmapc]: https://github.com/smkent/jmapc\n[logo]: https://raw.github.com/smkent/waffles/master/img/waffles.png\n[poetry]: https://python-poetry.org/docs/#installation\n[pypi]: https://pypi.org/project/wafflesbot/\n[replyowl]: https://github.com/smkent/replyowl\n[repo]: https://github.com/smkent/waffles\n',
    'author': 'Stephen Kent',
    'author_email': 'smkent@smkent.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/smkent/waffles',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
