# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['docspec_python']

package_data = \
{'': ['*']}

install_requires = \
['docspec>=2.0.0,<3.0.0', 'nr.util>=0.7.0']

entry_points = \
{'console_scripts': ['docspec-python = docspec_python.__main__:main']}

setup_kwargs = {
    'name': 'docspec-python',
    'version': '2.0.0',
    'description': 'A parser based on lib2to3 producing docspec data from Python source code.',
    'long_description': '  [docspec]: https://github.com/NiklasRosenstein/docspec\n\n# docspec-python\n\nA parser based on `lib2to3` procuding [docspec][] data from Python source code.\n\nExample:\n\n```\nfrom docspec_python import parse_python_module\nimport docspec, sys\ndocspec.dump_module(parse_python_module(sys.stdin, print_function=False), sys.stdout)\n```\n\n```\n$ docspec-python -p docspec | docspec --dump-tree --multiple | head\nmodule __init__\n| data __author__\n| data __version__\n| data __all__\n| data _ClassProxy\n| data _mapper\n| class Location\n| | data filename\n| | data lineno\n| class Decoration\n```\n\n---\n\n<p align="center">Copyright &copy; 2020, Niklas Rosenstein</p>\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/NiklasRosenstein/docspec/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
