# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_uri_parser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'data-uri-parser',
    'version': '0.1.8',
    'description': 'A Pythonic data uri parser',
    'long_description': '# data_uri_parser\n\n<a href="https://pypi.org/project/data_uri_parser/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/data_uri_parser.svg"></a>\n<a href="https://pypi.org/project/data_uri_parser/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/data_uri_parser.svg"></a>\n<a href="https://opensource.org/licenses/MIT"><img alt="Licence" src="https://img.shields.io/github/license/unmadeworks/data_uri_parser.svg"></a>\n\n_Data URI manipulation made easy._\n\nThis isn\'t very robust, and will reject a number of valid data URIs. However, it meets the most useful case: a mimetype, a charset, and the base64 flag.\n\n## How to install\n\n```sh\npip install data_uri_parser\n```\n\n### Parsing\n\n```python\n>>> uri = DataURI(\'data:text/plain;charset=utf-8;base64,VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wZWQgb3ZlciB0aGUgbGF6eSBkb2cu\')\n>>> uri.mimetype\n\'text/plain\'\n>>> uri.charset\n\'utf-8\'\n>>> uri.is_base64\nTrue\n>>> uri.data\n\'The quick brown fox jumped over the lazy dog.\'\n```\n\nNote that `DataURI.data` won\'t decode the data bytestring into a unicode string based on the charset.\n\n\n### Creating from a string\n\n```python\n>>> made = DataURI.make(\'text/plain\', charset=\'us-ascii\', base64=True, data=\'This is a message.\')\n>>> made\nDataURI(\'data:text/plain;charset=us-ascii;base64,VGhpcyBpcyBhIG1lc3NhZ2Uu\')\n>>> made.data\n\'This is a message.\'\n```\n\n\n### Creating from a file\n\nThis is really just a convenience method.\n\n```python\n>>> png_uri = DataURI.from_file(\'somefile.png\')\n>>> png_uri.mimetype\n\'image/png\'\n>>> png_uri.data\n\'\\x89PNG\\r\\n...\'\n```\n\n## Notes\n\nOriginally from: https://gist.github.com/zacharyvoase/5538178\n',
    'author': 'Unmade',
    'author_email': 'backend@unmade.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/unmadeworks/data_uri_parser/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
