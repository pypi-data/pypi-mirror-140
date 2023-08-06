# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['YetAnotherPicSearch']

package_data = \
{'': ['*']}

install_requires = \
['PicImageSearch>=2.2.6,<3.0.0',
 'arrow>=1.2.0,<2.0.0',
 'httpx>=0.18.0,<0.19.0',
 'nonebot-adapter-onebot>=2.0.0b1,<3.0.0',
 'nonebot2>=2.0.0b1,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pyquery>=1.4.3,<2.0.0',
 'tinydb>=4.6.1,<5.0.0']

setup_kwargs = {
    'name': 'yetanotherpicsearch',
    'version': '1.2.1',
    'description': 'Yet Another Picture Search Nonebot Plugin',
    'long_description': '# YetAnotherPicSearch\n\n基于 [nonebot/nonebot2](https://github.com/nonebot/nonebot2) 及 [kitUIN/PicImageSearch](https://github.com/kitUIN/PicImageSearch) 的另一个 Nonebot 搜图插件。\n\n目前适配的是 `OneBot V11` ，没适配 QQ 频道。\n\n主要受到 [Tsuk1ko/cq-picsearcher-bot](https://github.com/Tsuk1ko/cq-picsearcher-bot) 的启发，以及其遇到的问题 [Tsuk1ko/cq-picsearcher-bot#283](https://github.com/Tsuk1ko/cq-picsearcher-bot/issues/283) 不好解决。\n\n此外，我只需要基础的搜图功能，加上一些小调整，于是忍不住自己也写了一个。\n',
    'author': 'NekoAria',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NekoAria/YetAnotherPicSearch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
