# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['text2excel']

package_data = \
{'': ['*']}

install_requires = \
['openpyxl>=3.0.9,<4.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3,<5']}

entry_points = \
{'console_scripts': ['text2excel = text2excel.cli:main']}

setup_kwargs = {
    'name': 'text2excel',
    'version': '0.4.3',
    'description': 'Converts to Excel XLSX from a TSV or CSV text file.',
    'long_description': '# text2excel\n\n[myactions]: https://github.com/harkabeeparolus/text2excel/actions\n[mypypi]: https://pypi.org/project/text2excel/\n[mylicense]: https://github.com/harkabeeparolus/text2excel/blob/master/LICENSE\n[black]: https://github.com/psf/black\n\n[![Lint and Test](https://github.com/harkabeeparolus/text2excel/actions/workflows/python-package.yml/badge.svg)][myactions]\n[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/text2excel)][mypypi]\n[![PyPI](https://img.shields.io/pypi/v/text2excel)][mypypi]\n[![GitHub license](https://img.shields.io/github/license/harkabeeparolus/text2excel)][mylicense]\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n[![CodeQL](https://github.com/harkabeeparolus/text2excel/actions/workflows/codeql-analysis.yml/badge.svg)][myactions]\n\nThis program converts CSV Or TSV text files to Microsoft Excel format. It\nuses [openpyxl] to create Excel files.\n\nAs input it takes tab-separated `*.txt` files (TSV), or any CSV files\n(Comma-Separated Values) that can be auto-detected by the Python standard\nlibrary [csv] module.\n\n* You\'ll find the [text2excel source on GitHub][text2excel]\n\n[text2excel]: https://github.com/harkabeeparolus/text2excel\n[openpyxl]: https://openpyxl.readthedocs.io/\n[csv]: https://docs.python.org/3/library/csv.html\n\n## Example\n\n```bash\n$ printf "one\\ttwo\\tthree\\n1\\t2\\t3\\n" | tee my_data_file.txt\none two three\n1   2   3\n\n$ text2excel --numbers my_data_file.txt\nSaved to file: my_data_file.xlsx\n```\n\n## Installation\n\n[pipx]: https://github.com/pypa/pipx\n\nTo install or upgrade _text2excel_ from [PyPI][mypypi], I recommend using [pipx]:\n\n```bash\npipx install text2excel\npipx upgrade text2excel\n```\n\nIf you don\'t have _pipx_, you could also use _pip_ with your preferred Python version:\n\n```bash\npython3 -m pip install --user --upgrade-strategy eager --upgrade text2excel\n```\n\n## News\n\nPlease see the [changelog](CHANGELOG.md) for more details.\n\n## Contributing\n\nDo you want to help out with this project?\n\n* Please check the [CONTRIBUTING](CONTRIBUTING.md) guide.\n\n## Credits\n\nThis project was originally based on\n[a Gist by Konrad Förstner](https://gist.github.com/konrad/4154786).\n',
    'author': 'Fredrik Mellström',
    'author_email': '11281108+harkabeeparolus@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/harkabeeparolus/text2excel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
