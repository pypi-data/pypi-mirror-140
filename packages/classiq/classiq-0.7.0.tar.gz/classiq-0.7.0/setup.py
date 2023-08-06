# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classiq',
 'classiq._internals',
 'classiq._internals.authentication',
 'classiq.applications',
 'classiq.builtin_functions',
 'classiq.model_designer',
 'classiq.quantum_functions']

package_data = \
{'': ['*'], 'classiq': ['examples/*']}

install_requires = \
['ConfigArgParse>=1.5.3,<2.0.0',
 'Pyomo>=6.0,<6.1',
 'httpx>=0.22.0,<1',
 'keyring>=23.5.0,<24.0.0',
 'nest-asyncio>=1.5.4,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'semver>=2.13.0,<3.0.0',
 'websockets>=10.1,<11.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.11.1,<5.0.0'],
 'all': ['classiq-interface>=0.6.1,<0.7.0']}

setup_kwargs = {
    'name': 'classiq',
    'version': '0.7.0',
    'description': "Classiq's Python SDK for quantum computing",
    'long_description': '<p align="center">\n  <a href="https://www.classiq.io"><img src="https://uploads-ssl.webflow.com/60000db7a5f449af5e4590ac/6122b22eea7a9583a5c0d560_classiq_RGB_Green_with_margin.png\n" alt="Classiq"></a>\n</p>\n<p align="center">\n    <em>The Classiq Quantum Algorithm Design platform helps teams build sophisticated quantum circuits that could not be designed otherwise</em>\n</p>\n\nWe do this by synthesizing high-level functional models into optimized quantum\ncircuits, taking into account the constraints that are important to the designer.\nFurthermore, we are able to generate circuits for practically any universal gate-based\nquantum computer and are compatible with most quantum cloud providers.\n\nSee the\n[documentation](https://classiquantum.com/reference/getting-started/python-sdk.html)\nfor information about this extension.\n\n## License\n\nSee [license](https://classiq.io/license).\n',
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
