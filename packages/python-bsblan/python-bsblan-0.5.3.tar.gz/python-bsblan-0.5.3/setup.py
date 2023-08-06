# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bsblan']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'packaging>=21.3,<22.0',
 'pydantic>=1.9.0,<2.0.0',
 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'python-bsblan',
    'version': '0.5.3',
    'description': 'Asynchronous Python client for BSBLAN',
    'long_description': '# Python: BSBLan API Client\n\n[![GitHub Release][releases-shield]][releases]\n![Project Stage][project-stage-shield]\n![Project Maintenance][maintenance-shield]\n[![License][license-shield]](LICENSE.md)\n\n[![Build Status][build-shield]][build]\n[![Code Coverage][codecov-shield]][codecov]\n[![Code Quality][code-quality-shield]][code-quality]\n\n[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]\n\nAsynchronous Python client for BSBLan.\n\n## About\n\nThis package allows you to control and monitor an BSBLan device\nprogrammatically. It is mainly created to allow third-party programs to automate\nthe behavior of [BSBLan][bsblanmodule].\n\n## Installation\n\n```bash\npip install python-bsblan\n```\n\n## Usage\n\n```python\n# pylint: disable=W0621\n"""Asynchronous Python client for BSBLan."""\n\nimport asyncio\n\nfrom bsblan import BSBLan, Info, State\n\n\nasync def main(loop):\n    """Show example on controlling your BSBLan device.\n\n    Options:\n    - passkey (http://url/"passkey"/) if your device is setup for passkey authentication\n    - username and password if your device is setup for username/password authentication\n\n    """\n    async with BSBLan(\n        host="10.0.1.60", passkey=None, username=None, password=None, loop=loop\n    ) as bsblan:\n        # get state from bsblan device\n        state: State = await bsblan.state()\n        print(state)\n\n        # set temp thermostat\n        await bsblan.thermostat(target_temperature=19.0)\n\n        # set hvac_mode (0-3) (protection,auto,reduced,comfort)\n        await bsblan.thermostat(hvac_mode=3)\n\n        # get some generic info from the heater\n        info: Info = await bsblan.info()\n        print(info)\n\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.run_until_complete(main(loop))\n```\n\n## Changelog & Releases\n\nThis repository keeps a change log using [GitHub\'s releases][releases]\nfunctionality. The format of the log is based on\n[Keep a Changelog][keepchangelog].\n\nReleases are based on [Semantic Versioning][semver], and use the format\nof `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented\nbased on the following:\n\n- `MAJOR`: Incompatible or major changes.\n- `MINOR`: Backwards-compatible new features and enhancements.\n- `PATCH`: Backwards-compatible bugfixes and package updates.\n\n## Contributing\n\nThis is an active open-source project. We are always open to people who want to\nuse the code or contribute to it.\n\nWe\'ve set up a separate document for our\n[contribution guidelines](CONTRIBUTING.md).\n\nThank you for being involved! :heart_eyes:\n\n## Setting up development environment\n\nThis Python project is fully managed using the [Poetry][poetry] dependency manager. But also relies on the use of NodeJS for certain checks during development.\n\nYou need at least:\n\n- Python 3.9+\n- [Poetry][poetry-install]\n- NodeJS 16+ (including NPM)\n\nTo install all packages, including all development requirements:\n\n```bash\nnpm install\npoetry install\n```\n\nAs this repository uses the [pre-commit][pre-commit] framework, all changes\nare linted and tested with each commit. You can run all checks and tests\nmanually, using the following command:\n\n```bash\npoetry run pre-commit run --all-files\n```\n\nTo run just the Python tests:\n\n```bash\npoetry run pytest\n```\n\n## Authors & contributors\n\nThe template is from the repository \'elgato\' by [Franck Nijhof][frenck].\nThe setup of this repository is by [Willem-Jan van Rootselaar][liudger].\n\nFor a full list of all authors and contributors,\ncheck [the contributor\'s page][contributors].\n\n## License\n\nMIT License\n\nCopyright (c) 2022 WJ van Rootselaar\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n\n[bsblanmodule]: https://github.com/fredlcore/bsb_lan\n[build-shield]: https://github.com/liudger/python-bsblan/workflows/Continuous%20Integration/badge.svg\n[build]: https://github.com/liudger/python-bsblan/actions\n[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg\n[buymeacoffee]: https://www.buymeacoffee.com/liudger\n[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/liudger/python-bsblan.svg?logo=lgtm&logoWidth=18\n[code-quality]: https://lgtm.com/projects/g/liudger/python-bsblan/context:python\n[codecov-shield]: https://codecov.io/gh/liudger/python-bsblan/branch/Dev/graph/badge.svg?token=ypos87GGxv\n[codecov]: https://codecov.io/gh/liudger/python-bsblan\n[contributors]: https://github.com/liudger/python-bsblan/graphs/contributors\n[frenck]: https://github.com/frenck\n[keepchangelog]: http://keepachangelog.com/en/1.0.0/\n[license-shield]: https://img.shields.io/github/license/liudger/python-bsblan.svg\n[liudger]: https://github.com/liudger\n[live-coding]: https://www.youtube.com/watch?v=6LHeoUS1R40\n[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg\n[poetry]: https://python-poetry.org\n[poetry-install]: https://python-poetry.org/docs/#installation\n[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg\n[releases-shield]: https://img.shields.io/github/v/release/liudger/python-bsblan.svg\n[releases]: https://github.com/liudger/python-bsblan/releases\n[semver]: http://semver.org/spec/v2.0.0.html\n',
    'author': 'Willem-Jan van Rootselaar',
    'author_email': 'liudgervr@gmail.com',
    'maintainer': 'Willem-Jan van Rootselaar',
    'maintainer_email': 'liudgervr@gmail.com',
    'url': 'https://github.com/liudger/python-bsblan',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
