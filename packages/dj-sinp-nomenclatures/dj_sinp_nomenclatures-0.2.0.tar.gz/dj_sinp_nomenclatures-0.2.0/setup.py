# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sinp_nomenclatures', 'sinp_nomenclatures.migrations']

package_data = \
{'': ['*'], 'sinp_nomenclatures': ['fixtures/*']}

install_requires = \
['Django>=4.0.2,<5.0.0', 'django-rest-framework>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'dj-sinp-nomenclatures',
    'version': '0.2.0',
    'description': 'Django app to manage french SINP nomenclatures standards',
    'long_description': 'DjangoSinpNomenclature\n======================\n\n\nA simple django reusable app to manage French SINP nomenclature repository\n\n\n',
    'author': 'dbChiro project',
    'author_email': 'project@dbchiro.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dbchiro/DjangoSinpNomenclature',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
