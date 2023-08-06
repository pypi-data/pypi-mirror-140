# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chope_data_haidilao',
 'chope_data_haidilao.entity_values',
 'chope_data_haidilao.pattern',
 'chope_data_haidilao.request',
 'chope_data_haidilao.retrieval']

package_data = \
{'': ['*'],
 'chope_data_haidilao': ['conf/*', 'conf/env/*', 'conf/feature_store/*']}

install_requires = \
['cloudpickle==2.0.0',
 'google-cloud-aiplatform>=1.6.0,<2.0.0',
 'google-cloud-bigquery',
 'google-cloud-bigquery-storage>=2.10.1,<3.0.0',
 'google-cloud-storage',
 'hydra-core',
 'pandas',
 'pyarrow',
 'python-dotenv']

setup_kwargs = {
    'name': 'chope-data-haidilao',
    'version': '0.1.0',
    'description': 'Featurestore wrapper',
    'long_description': None,
    'author': 'Quy Dinh',
    'author_email': 'quy.d@chope.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
