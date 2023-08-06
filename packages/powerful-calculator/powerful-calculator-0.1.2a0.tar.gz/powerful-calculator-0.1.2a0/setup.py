# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['powerful_calculator']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cli_command_name = package_name:function']}

setup_kwargs = {
    'name': 'powerful-calculator',
    'version': '0.1.2a0',
    'description': 'Calculator for basic operation',
    'long_description': '## Installation\n\n```sh\npip install numpy\npip install powerfull-calculator\n```\n\n## Usage\n\nWith use of this tool you can:\n\n-  add numbers - via add() metod\n-  subtract numbers - via subtract() metod\n-  multiply numbers - via multiply() metod\n-  divide numbers - via divide() metod\n-  root numbers - root add() metod\n## Before start using\n\nThere is always number in memory of calculator.\nOperations are perfomed on this number.\nYou can get it via get_state() method.\n\n```python\n>>> calc = Calculator()\n>>> calc.add(0.1)\n0.1\n>>> calc.add(0.2)\n0.3\n>>> calc.subtract(10.3)\n-10.0\n>>> calc.divide(3)\n-3.333333333333\n>>> calc.multiply(3)\n-10.0\n>>> calc.root(1/3)\n-1000.0\n>>> calc.reset()\n0.0\n>>> calc.get_state()\n0.0\n```\n\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nMake sure to add or update tests as appropriate.\n\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'Dawid Konard Kohnke',
    'author_email': 'dawid.kohnke.cad@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/anytokin/calculator',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
