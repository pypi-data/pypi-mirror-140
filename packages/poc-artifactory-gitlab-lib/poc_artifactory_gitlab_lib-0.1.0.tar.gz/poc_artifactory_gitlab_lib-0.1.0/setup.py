# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poc_artifactory_gitlab_lib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'poc-artifactory-gitlab-lib',
    'version': '0.1.0',
    'description': 'Gitlab-CI POC project.',
    'long_description': None,
    'author': 'Pierre-Yves Gillier',
    'author_email': 'pierre-yves.gillier@jellysmack.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
