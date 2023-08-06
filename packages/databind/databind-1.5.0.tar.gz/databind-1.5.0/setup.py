# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['_version']

package_data = \
{'': ['*']}

install_requires = \
['databind.core>=1.5.0,<2.0.0', 'databind.json>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'databind',
    'version': '1.5.0',
    'description': 'Databind is a library inspired by jackson-databind to de-/serialize Python dataclasses. The `databind` package will install the full suite of databind packages. Compatible with Python 3.7 and newer.',
    'long_description': '# databind\n\nDatabind is a library inspired by jackson-databind to de-/serialize Python dataclasses. The `databind` package\nwill install the full suite of databind packages. Compatible with Python 3.7 and newer.\n\n* [databind.core](https://pypi.org/project/databind.core/) &ndash; Provides the core framework.\n* [databind.json](https://pypi.org/project/databind.json/) &ndash; De-/serialize dataclasses to/from JSON payloads.\n\n## Supported features\n\n| Feature | Python version | Databind version |\n| ------- | -------------- | ---------------- |\n| [PEP585](https://www.python.org/dev/peps/pep-0585/) | 3.9 | 1.2.0 &ndash; *current* |\n| [PEP585](https://www.python.org/dev/peps/pep-0585/) (forward references) | 3.9 | 1.3.1? &ndash; *current* |\n| Resolve type parameters of specialized generic types | 3.x | 1.5.0 &ndash; *current* |\n\n---\n\n<p align="center">Copyright &copy; 2022 &ndash; Niklas Rosenstein</p>\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
