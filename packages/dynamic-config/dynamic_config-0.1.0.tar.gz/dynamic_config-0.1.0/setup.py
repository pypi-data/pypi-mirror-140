# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamic_config']

package_data = \
{'': ['*']}

install_requires = \
['redis>=4.1.4,<5.0.0']

setup_kwargs = {
    'name': 'dynamic-config',
    'version': '0.1.0',
    'description': 'Distributed dynamic configuration based on Redis',
    'long_description': '### dynamic_config \n- name = "dynamic_config"\n- description = "Distributed dynamic configuration based on Redis"\n- authors = ["Euraxluo <euraxluo@qq.com>"]\n- license = "The MIT LICENSE"\n- repository = "https://github.com/Euraxluo/dynamic_config"\n\n#### install\n`pip install dynamic-config`\n\n#### UseAge\n```\nfrom dynamic_config.dynamic_config import DynamicConfig, Filed\nfrom example.conftest import rdb\nfrom loguru import logger\n\nDynamicConfig.register(rdb,logger=logger)\n\nclass ConfigTest(DynamicConfig):\n    __prefix__ = "test_config"\n    __enable__ = True\n    x: str = None\n    y: str = Filed(None)\n\nprint(ConfigTest.x)\nprint(ConfigTest.y)\nConfigTest.x = 10\nConfigTest.y = [1,2,3,4]\n```',
    'author': 'Euraxluo',
    'author_email': 'euraxluo@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Euraxluo/dynamic_config',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
