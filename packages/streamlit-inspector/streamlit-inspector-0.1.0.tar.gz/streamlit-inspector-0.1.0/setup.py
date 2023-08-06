# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_inspector']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.11.2,<3.0.0',
 'streamlit>=1.6.0,<2.0.0',
 'validators>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'streamlit-inspector',
    'version': '0.1.0',
    'description': '🕵️ Streamlit component to inspect Python objects during development',
    'long_description': None,
    'author': 'Johannes Rieke',
    'author_email': 'johannes.rieke@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
