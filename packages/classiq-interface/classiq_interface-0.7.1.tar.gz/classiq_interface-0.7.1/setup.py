# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classiq_interface',
 'classiq_interface.analyzer',
 'classiq_interface.backend',
 'classiq_interface.backend.ionq',
 'classiq_interface.chemistry',
 'classiq_interface.combinatorial_optimization',
 'classiq_interface.combinatorial_optimization.examples',
 'classiq_interface.executor',
 'classiq_interface.finance',
 'classiq_interface.generator',
 'classiq_interface.generator.arith',
 'classiq_interface.generator.credit_risk_example',
 'classiq_interface.generator.functions',
 'classiq_interface.generator.model',
 'classiq_interface.generator.model.preferences',
 'classiq_interface.generator.preferences',
 'classiq_interface.generator.standard_gates',
 'classiq_interface.generator.validations',
 'classiq_interface.helpers',
 'classiq_interface.pyomo_extension',
 'classiq_interface.server']

package_data = \
{'': ['*']}

install_requires = \
['Pyomo>=6.0,<6.1',
 'matplotlib>=3.4.3,<4.0.0',
 'more-itertools>=8.8.0,<9.0.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pillow>=9.0.0,<10.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'qiskit-terra>=0.19.1,<1',
 'tabulate>=0.8.9,<1']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.1,<5.0.0']}

setup_kwargs = {
    'name': 'classiq-interface',
    'version': '0.7.1',
    'description': 'Classiq Interface',
    'long_description': 'See [classiq package](https://pypi.org/project/classiq/) README.\n\n### License\n\nSee [license](https://classiq.io/license).\n',
    'author': 'Classiq Technologies',
    'author_email': 'support@classiq.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://classiq.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
