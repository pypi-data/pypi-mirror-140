# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opennews']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp', 'requests']

setup_kwargs = {
    'name': 'opennews',
    'version': '0.0.2',
    'description': 'An open source scraper to get current news.',
    'long_description': "# OpenNews\n\n### An open source news scraper (soon to be an API)\n\n## Usage\n\n```py\nimport opennews\n\nopennews.get_all_news()\n# {'https://lite.cnn.com/en/en/article/h_dba861346d41e987119c7dd582b9ce26': 'Kyiv: Ukrainians fight to keep control of their capital', 'https://lite.cnn.com/en/en/article/h_9a2e01ad1a0d0ad6bae3da70a986ac89': 'Analysis: US intelligence got it right on Ukraine', 'https://lite.cnn.com/en/en/article/h_13235222fe8a657308f4e2e716cd4aa7': ...\n```\n\nIt also supports async\n```py\nimport opennews\nimport asyncio\n\nasyncio.run(opennews.get_all_news_async())\n# {'https://lite.cnn.com/en/en/article/h_dba861346d41e987119c7dd582b9ce26': 'Kyiv: Ukrainians fight to keep control of their capital', 'https://lite.cnn.com/en/en/article/h_9a2e01ad1a0d0ad6bae3da70a986ac89': 'Analysis: US intelligence got it right on Ukraine', 'https://lite.cnn.com/en/en/article/h_13235222fe8a657308f4e2e716cd4aa7': ...\n```\n\nThe scraper currently only scrapes from \n- CNBC (`cnbc`)\n- CNN (`cnn`)\n- Fox News (`fox`)\n- MSNBC (`msnbc`)\n- NBC News (`nbc`)\n- The New York Times (`nytimes`)\n- Reuters (`reuters`)\n- The Guardian (`theguardian`)\n- USA Today (`usatoday`)\n- The Washington Post (`washingtonpost`)\n- The Wall Street Journal <sub>(not able to scrape all links- currently being worked on)</sub> (`wsj`)\n\nIf you want to use one of these, you may do\n```py\nimport opennews\n\nopennews.cnn.get_news()\n\n# This supports async too!\n\nimport asyncio\n\nasyncio.run(opennews.cnn.get_news_async())\n```\n\n\n## License\nThis repository is under the LGPL License as described in the LICENSE file.\n\n\n## Contributing\nPlease open a PR on GitHub if you want to contribute!\n\n## Todo\n\n- [ ] Add more sources\n- [ ] Make an API\n- [ ] Make deeper search to find thumbnail, content, etc.\n",
    'author': 'Zeb Taylor',
    'author_email': 'zceboys@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/foxnerdsaysmoo/opennews',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
