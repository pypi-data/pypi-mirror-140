# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hibiapi',
 'hibiapi.api',
 'hibiapi.api.bilibili',
 'hibiapi.api.bilibili.api',
 'hibiapi.api.netease',
 'hibiapi.api.pixiv',
 'hibiapi.api.sauce',
 'hibiapi.api.tieba',
 'hibiapi.api.wallpaper',
 'hibiapi.app',
 'hibiapi.app.routes',
 'hibiapi.app.routes.bilibili',
 'hibiapi.utils',
 'hibiapi.utils.decorators']

package_data = \
{'': ['*'], 'hibiapi': ['configs/*']}

install_requires = \
['aiocache>=0.11.1,<0.12.0',
 'click>=8.0.1,<9.0.0',
 'confuse>=1.4.0,<2.0.0',
 'fastapi>=0.71.0,<0.72.0',
 'httpx[http2]>=0.21.3,<0.23.0',
 'loguru>=0.5.3,<0.7.0',
 'pycryptodomex>=3.10.1,<4.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dotenv>=0.17,<0.20',
 'python-multipart>=0.0.5,<0.0.6',
 'qrcode[pil]>=6.1,<8.0',
 'sentry-sdk>=1.5.0,<2.0.0',
 'uvicorn[standard]>=0.14,<0.18']

entry_points = \
{'console_scripts': ['hibiapi = hibiapi.__main__:main']}

setup_kwargs = {
    'name': 'hibiapi',
    'version': '0.7.7',
    'description': 'A program that implements easy-to-use APIs for a variety of commonly used sites',
    'long_description': '<!-- spell-checker: disable -->\n<!-- markdownlint-disable MD033 MD041 -->\n\n<img src=".github/logo.svg" align="right">\n\n<div align="left">\n\n# HibiAPI\n\n**_一个实现了多种常用站点的易用化API的程序._**\n\n**_A program that implements easy-to-use APIs for a variety of commonly used sites._**\n\n[![Demo Version](https://img.shields.io/badge/dynamic/json?label=demo%20status&query=%24.info.version&url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json&style=for-the-badge&color=lightblue)](https://api.obfs.dev)\n\n![Lint](https://github.com/mixmoe/HibiAPI/workflows/Lint/badge.svg)\n![Test](https://github.com/mixmoe/HibiAPI/workflows/Test/badge.svg)\n[![Coverage](https://codecov.io/gh/mixmoe/HibiAPI/branch/main/graph/badge.svg)](https://codecov.io/gh/mixmoe/HibiAPI)\n\n[![PyPI](https://img.shields.io/pypi/v/hibiapi)](https://pypi.org/project/hibiapi/)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/hibiapi)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hibiapi)\n![PyPI - License](https://img.shields.io/pypi/l/hibiapi)\n\n![GitHub last commit](https://img.shields.io/github/last-commit/mixmoe/HibiAPI)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mixmoe/hibiapi)\n![Lines of code](https://img.shields.io/tokei/lines/github/mixmoe/hibiapi)\n[![GitHub stars](https://img.shields.io/github/stars/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/stargazers)\n[![GitHub forks](https://img.shields.io/github/forks/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/network)\n[![GitHub issues](https://img.shields.io/github/issues/mixmoe/HibiAPI)](https://github.com/mixmoe/HibiAPI/issues)\n\n</div>\n\n---\n\n## 前言\n\n- `HibiAPI`提供多种网站公开内容的API集合, 它们包括:\n  - Pixiv的图片和小说相关信息获取和搜索\n  - Bilibili的视频/番剧等信息获取和搜索\n  - 网易云音乐的音乐/MV等信息获取和搜索\n  - 百度贴吧的帖子内容的获取\n  - [爱壁纸](https://adesk.com/)的横版和竖版壁纸获取\n  - and more…\n\n- 该项目的前身是 Imjad API[^1]\n  - 由于它的使用人数过多, 致使调用超出限制, 所以本人希望提供一个开源替代来供社区进行自由地部署和使用, 从而减轻一部分该 API 的使用压力\n\n[^1]: [什么是Imjad API](https://github.com/mixmoe/HibiAPI/wiki/FAQ#%E4%BB%80%E4%B9%88%E6%98%AFimjad-api)\n\n## 优势\n\n### 开源\n\n- 本项目以[Apache-2.0](./LICENSE)许可开源, 即:\n  - 你可以直接使用该项目提供的功能, 无需任何授权\n  - 你可以在**注明来源版权信息**的情况下对源代码进行任意分发和修改以及衍生\n\n### 高效\n\n- 使用 Python 的[异步机制](https://docs.python.org/zh-cn/3/library/asyncio.html), 由[FastAPI](https://fastapi.tiangolo.com/)驱动, 带来高效的使用体验 ~~虽然性能瓶颈压根不在这~~\n\n### 稳定\n\n- 在代码中广泛使用了Python的[类型提示支持](https://docs.python.org/zh-cn/3/library/typing.html), 使代码可读性更高且更加易于维护和调试\n\n- 在开发初期起就一直使用[PyLance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Flake8](https://flake8.pycqa.org/en/latest/)以及[MyPy](https://mypy.readthedocs.io/)来对代码进行类型推断和纠错\n\n- 不直接使用第三方开发的 API 调用库, 而是全部用更加适合 Web 应用的逻辑重写第三方 API 请求, 更加可控 ~~疯狂造轮子~~\n\n## 已实现API[^2]\n\n[^2]: 请查看 [#1](https://github.com/mixmoe/HibiAPI/issues/1)\n\n- [x] Pixiv\n- [x] 网易云音乐\n- [ ] ~~一言~~ (其代替方案<https://hitokoto.cn>提供的方案已足够好, 暂不考虑支持)\n- [x] Bilibili\n- [x] 二维码\n- [ ] ~~企鹅FM~~ (似乎用的人不是很多)\n- [x] 百度贴吧\n- [x] 爱壁纸\n\n## 部署指南\n\n[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)\n\n- 手动部署指南: **[点击此处查看](https://github.com/mixmoe/HibiAPI/wiki/Deployment)**\n\n## 应用实例\n\n**我有更多的应用实例?** [立即 PR!](https://github.com/mixmoe/HibiAPI/pulls)\n\n- [`journey-ad/pixiv-viewer`](https://github.com/journey-ad/pixiv-viewer)\n\n  - **又一个 Pixiv 阅览工具**\n\n- 公开搭建实例\n  |         **站点名称**         |            **网址**             |        **状态**         |\n  | :--------------------------: | :-----------------------------: | :---------------------: |\n  |      **官方 Demo[^3]**       |     <https://api.obfs.dev>      |  ![official][official]  |\n  |           轻零 API           |   <https://hibiapi.lite0.com>   |     ![lite0][lite0]     |\n  |     Kyomotoi の菜几服务      |   <https://api.kyomotoi.moe>    |       ![kyo][kyo]       |\n  |          老狐狸 API          | <https://hibiapi.aliserver.net> | ![older-fox][older-fox] |\n  | [MyCard](https://mycard.moe) |   <https://hibi.moecube.com>    |    ![mycard][mycard]    |\n\n[^3]: 为了减轻服务器负担, Demo服务器已开启了Cloudflare全站缓存, 如果有实时获取更新的需求, 请自行搭建或使用其他部署实例\n\n[official]: https://img.shields.io/website?url=https%3A%2F%2Fapi.obfs.dev%2Fopenapi.json\n[lite0]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.lite0.com%2Fopenapi.json\n[kyo]: https://img.shields.io/website?url=https%3A%2F%2Fapi.kyomotoi.moe%2Fopenapi.json\n[older-fox]: https://img.shields.io/website?url=https%3A%2F%2Fhibiapi.aliserver.net%2Fopenapi.json\n[mycard]: https://img.shields.io/website?url=https%3A%2F%2Fhibi.moecube.com%2Fopenapi.json\n\n## 特别鸣谢\n\n[**@journey-ad**](https://github.com/journey-ad) 大佬的 [Imjad API](https://api.imjad.cn/)\n\n### 参考项目\n\n> **正是因为有了你们, 这个项目才得以存在**\n\n- Pixiv: [`Mikubill/pixivpy-async`](https://github.com/Mikubill/pixivpy-async) [`upbit/pixivpy`](https://github.com/upbit/pixivpy)\n\n- Bilibili: [`SocialSisterYi/bilibili-API-collect`](https://github.com/SocialSisterYi/bilibili-API-collect) [`soimort/you-get`](https://github.com/soimort/you-get)\n\n- 网易云音乐: [`metowolf/NeteaseCloudMusicApi`](https://github.com/metowolf/NeteaseCloudMusicApi) [`greats3an/pyncm`](https://github.com/greats3an/pyncm) [`Binaryify/NeteaseCloudMusicApi`](https://github.com/Binaryify/NeteaseCloudMusicApi)\n\n- 百度贴吧: [`libsgh/tieba-api`](https://github.com/libsgh/tieba-api)\n\n### 贡献者们\n\n<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->\n[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)\n<!-- ALL-CONTRIBUTORS-BADGE:END -->\n\n感谢这些为这个项目作出贡献的各位大佬:\n\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n<table>\n  <tr>\n    <td align="center"><a href="http://kyomotoi.moe"><img src="https://avatars.githubusercontent.com/u/37587870?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kyomotoi</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Documentation">📖</a> <a href="https://github.com/mixmoe/HibiAPI/commits?author=Kyomotoi" title="Tests">⚠️</a></td>\n    <td align="center"><a href="http://thdog.moe"><img src="https://avatars.githubusercontent.com/u/46120251?v=4?s=100" width="100px;" alt=""/><br /><sub><b>城倉奏</b></sub></a><br /><a href="#example-shirokurakana" title="Examples">💡</a></td>\n    <td align="center"><a href="http://skipm4.com"><img src="https://avatars.githubusercontent.com/u/40311581?v=4?s=100" width="100px;" alt=""/><br /><sub><b>SkipM4</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=SkipM4" title="Documentation">📖</a></td>\n    <td align="center"><a href="https://github.com/leaf7th"><img src="https://avatars.githubusercontent.com/u/38352552?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nook</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=leaf7th" title="Code">💻</a></td>\n    <td align="center"><a href="https://github.com/jiangzhuochi"><img src="https://avatars.githubusercontent.com/u/50538375?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jocky Chiang</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=jiangzhuochi" title="Code">💻</a></td>\n    <td align="center"><a href="https://github.com/cleoold"><img src="https://avatars.githubusercontent.com/u/13920903?v=4?s=100" width="100px;" alt=""/><br /><sub><b>midori</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=cleoold" title="Documentation">📖</a></td>\n    <td align="center"><a href="https://www.2yo.cc"><img src="https://avatars.githubusercontent.com/u/41198038?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Pretty9</b></sub></a><br /><a href="https://github.com/mixmoe/HibiAPI/commits?author=Pretty9" title="Code">💻</a></td>\n  </tr>\n</table>\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n\n_本段符合 [all-contributors](https://github.com/all-contributors/all-contributors) 规范_\n\n## 联系方式\n\n- 邮箱: <admin@obfs.dev>\n\n## 开源许可\n\n    Copyright 2020-2021 Mix Technology\n\n    Licensed under the Apache License, Version 2.0 (the "License");\n    you may not use this file except in compliance with the License.\n    You may obtain a copy of the License at\n\n        http://www.apache.org/licenses/LICENSE-2.0\n\n    Unless required by applicable law or agreed to in writing, software\n    distributed under the License is distributed on an "AS IS" BASIS,\n    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n    See the License for the specific language governing permissions and\n    limitations under the License.\n',
    'author': 'mixmoe',
    'author_email': 'admin@obfs.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://api.obfs.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
