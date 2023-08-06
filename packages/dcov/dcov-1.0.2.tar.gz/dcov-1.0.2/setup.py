# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dcov', 'dcov.violationsreporters']

package_data = \
{'': ['*'], 'dcov': ['templates/*']}

install_requires = \
['Jinja2>=2.7.1',
 'Pygments>=2.9.0,<3.0.0',
 'chardet>=3.0.0',
 'pluggy>=0.13.1,<2']

extras_require = \
{':python_version < "3.8"': ['setuptools>=17.0.0'],
 'toml': ['tomli>=1.2.1,<2.0.0']}

entry_points = \
{'console_scripts': ['dcov = dcov.diff_cover_tool:main',
                     'dcov-quality = dcov.diff_quality_tool:main']}

setup_kwargs = {
    'name': 'dcov',
    'version': '1.0.2',
    'description': 'Modify output info when no compare-branch provided',
    'long_description': 'Diff Coverage\n=============\n\nDiff Coverage is forked from [diff_cover](https://github.com/Bachmann1234/diff_cover)\n\nThank Bachmann1234\n',
    'author': 'See Contributors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xiak/dcov',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
