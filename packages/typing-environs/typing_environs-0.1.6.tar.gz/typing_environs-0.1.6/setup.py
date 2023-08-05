# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['typing_environs']

package_data = \
{'': ['*']}

install_requires = \
['easydict>=1.9,<2.0', 'environs>=9.5.0,<10.0.0', 'pydantic>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'typing-environs',
    'version': '0.1.6',
    'description': 'typing_environs add type hints support  for environs',
    'long_description': '### typing_environs \n- name = "typing_environs"\n- description = "typing_environs add type hints support  for environs"\n- authors = ["Euraxluo <euraxluo@qq.com>"]\n- license = "The MIT LICENSE"\n- repository = "https://github.com/Euraxluo/typing_environs"\n\n#### install\n`pip install typing-environs`\n\n#### UseAge\n```\nfrom typing_environs import EnvModule, Types\n\n\nclass FLS(EnvModule):\n    open: Types.bool\n    level: Types.upper\n    dir: Types.dir\n    rotation: Types.str\n    retention: Types.str\n    compression: Types.str\n    encoding: Types.str\n    enqueue: Types.bool\n    backtrace: Types.bool\n    diagnose: Types.bool\n\n\nclass Log(EnvModule):\n    format: Types.str\n    dir: Types.dir\n    level: Types.upper\n    fls: FLS\n\n\nclass Config(EnvModule):  # 默认配置\n    env: Types.str\n    application: Types.str\n    version: Types.str\n    data_separator: Types.str\n\n    log: Log\n\n    def __init__(self, *args, paths=["default.env"], **kwargs):\n        super(Config, self).__init__(*args, paths=paths, **kwargs)\n```',
    'author': 'Euraxluo',
    'author_email': 'euraxluo@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Euraxluo/typing_environs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
