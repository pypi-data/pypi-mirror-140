# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['irmin']

package_data = \
{'': ['*']}

install_requires = \
['cffi>=1.15.0,<2.0.0']

setup_kwargs = {
    'name': 'irmin',
    'version': '0.3.1b0',
    'description': 'Irmin bindings for Python',
    'long_description': "# irmin-py\n\n[irmin](https://irmin.org) bindings for Python\n\nThis crate enables you to call directly into irmin from your Python application and\ncan be used to open an existing irmin store from Python that may have been created\nby an application written in OCaml.\n\n## Dependencies\n\n- `cffi`\n- `pytest` (for testing)\n\n## Installation\n\nAfter installing [libirmin](https://github.com/mirage/irmin) using opam, you can run:\n\n```\n$ pip3 install git+https://github.com/mirage/irmin-py.git --user\n```\n\nOr from the root of the project:\n\nUsing pip:\n```\n$ pip3 install . --user\n```\n\nUsing poetry:\n```\n$ POETRY_VIRTUALENVS_CREATE=false poetry install\n```\n\nAnd the build script should be able to find the location of the `libirmin` library and header files.\n\nIf `libirmin.so` and `irmin.h` were not installed using opam and they're not in `~/.local` or\n`/usr/local`, then you can specify where to look for them using the `LIBIRMIN_PREFIX` env\nvariable.\n\n## Testing\n\nRun the tests:\n\n```\n$ poetry run pytest\n```\n",
    'author': 'Zach Shipko',
    'author_email': 'zachshipko@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mirage/irmin-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
