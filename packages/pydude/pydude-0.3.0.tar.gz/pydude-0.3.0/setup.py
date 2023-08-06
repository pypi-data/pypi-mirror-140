# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dude']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'playwright>=1.19.0,<2.0.0']

extras_require = \
{'bs4': ['beautifulsoup4>=4.10.0,<5.0.0', 'httpx>=0.22.0,<0.23.0']}

entry_points = \
{'console_scripts': ['dude = dude:cli']}

setup_kwargs = {
    'name': 'pydude',
    'version': '0.3.0',
    'description': 'dude uncomplicated data extraction',
    'long_description': '<table>\n    <tr>\n        <td>License</td>\n        <td><img src=\'https://img.shields.io/pypi/l/pydude.svg?style=for-the-badge\' alt="License"></td>\n        <td>Version</td>\n        <td><img src=\'https://img.shields.io/pypi/v/pydude.svg?logo=pypi&style=for-the-badge\' alt="Version"></td>\n    </tr>\n    <tr>\n        <td>Github Actions</td>\n        <td><img src=\'https://img.shields.io/github/workflow/status/roniemartinez/dude/Python?label=actions&logo=github%20actions&style=for-the-badge\' alt="Github Actions"></td>\n        <td>Coverage</td>\n        <td><img src=\'https://img.shields.io/codecov/c/github/roniemartinez/dude/branch?label=codecov&logo=codecov&style=for-the-badge\' alt="CodeCov"></td>\n    </tr>\n    <tr>\n        <td>Supported versions</td>\n        <td><img src=\'https://img.shields.io/pypi/pyversions/pydude.svg?logo=python&style=for-the-badge\' alt="Python Versions"></td>\n        <td>Wheel</td>\n        <td><img src=\'https://img.shields.io/pypi/wheel/pydude.svg?style=for-the-badge\' alt="Wheel"></td>\n    </tr>\n    <tr>\n        <td>Status</td>\n        <td><img src=\'https://img.shields.io/pypi/status/pydude.svg?style=for-the-badge\' alt="Status"></td>\n        <td>Downloads</td>\n        <td><img src=\'https://img.shields.io/pypi/dm/pydude.svg?style=for-the-badge\' alt="Downloads"></td>\n    </tr>\n</table>\n\n# dude uncomplicated data extraction\n\nDude is a very simple framework for writing a web scraper using Python decorators.\nThe design, inspired by [Flask](https://github.com/pallets/flask), was to easily build a web scraper in just a few lines of code.\nDude has an easy to learn syntax.\n\n> 🚨 Dude is currently in Pre-Alpha. Please expect breaking changes.\n\n## Minimal web scraper\n\nThe simplest web scraper will look like this:\n\n```python\nfrom dude import select\n\n\n@select(selector="a")\ndef get_link(element):\n    return {"url": element.get_attribute("href")}\n```\n\nThe example above will get all the [hyperlink](https://en.wikipedia.org/wiki/Hyperlink#HTML) elements in a page and calls the handler function `get_link()` for each element.\nTo start scraping, just simply run in your terminal:\n\n## How to run the scraper\n\nYou can run your scraper from terminal/shell/command-line by supplying URLs, the output filename of your choice and the paths to your python codes to `dude scrape` command.\n\n```bash\ndude scrape --url "<url>" --output data.json path/to/file.py #(1)\n```\n\n## Features\n\n- Simple [Flask](https://github.com/pallets/flask)-inspired design - build a scraper with decorators.\n- Uses [Playwright](https://playwright.dev/python/) API - run your scraper in Chrome, Firefox and Webkit and leverage Playwright\'s powerful selector engine supporting CSS, XPath, text, regex, etc.\n- Data grouping - group related scraping data.\n- URL pattern matching - run functions on specific URLs.\n- Priority - reorder functions based on priority.\n- Setup function - enable setup steps (clicking dialogs or login).\n- Navigate function - enable navigation steps to move to other pages.\n- Custom storage - option to save data to other formats or database.\n- Async support - write async handlers.\n- BeautifulSoup4 - option to use BeautifulSoup4 instead of Playwright.\n\n## Documentation\n\nRead the complete documentation at [https://roniemartinez.github.io/dude/](https://roniemartinez.github.io/dude/).\nAll the advanced and useful features are documented there.\n\n## Support\n\nThis project is at a very early stage. This dude needs some love! ❤️\n\nContribute to this project by feature requests, idea discussions, reporting bugs, opening pull requests, or through Github Sponsors. Your help is highly appreciated.\n\n[![Github Sponsors](https://img.shields.io/github/sponsors/roniemartinez?label=github%20sponsors&logo=github%20sponsors&style=for-the-badge)](https://github.com/sponsors/roniemartinez)\n\n## Requirements\n\n- ✅ Any dude should know how to work with selectors (CSS or XPath).\n- ✅ This library was built on top of [Playwright](https://github.com/microsoft/playwright-python). Any dude should be at least familiar with the basics of Playwright - they also extended the selectors to support text, regular expressions, etc. See [Selectors | Playwright Python](https://playwright.dev/python/docs/selectors).\n- ✅ Python decorators... you\'ll live, dude!\n\n## Why name this project "dude"?\n\n- ✅ A [Recursive acronym](https://en.wikipedia.org/wiki/Recursive_acronym) looks nice.\n- ✅ Adding "uncomplicated" (like [`ufw`](https://wiki.ubuntu.com/UncomplicatedFirewall)) into the name says it is a very simple framework. \n- ✅ Puns! I also think that if you want to do web scraping, there\'s probably some random dude around the corner who can make it very easy for you to start with it. 😊\n\n## Author\n\n[Ronie Martinez](mailto:ronmarti18@gmail.com)\n',
    'author': 'Ronie Martinez',
    'author_email': 'ronmarti18@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/roniemartinez/dude',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
