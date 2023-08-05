# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_petpet']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.2.0',
 'aiocache>=0.11.0',
 'httpx>=0.19.0',
 'imageio>=2.12.0,<3.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'numpy>=1.20.0,<2.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-petpet',
    'version': '0.2.6.1',
    'description': 'Nonebot2 plugin for making fun pictures',
    'long_description': '# nonebot-plugin-petpet\n\n[Nonebot2](https://github.com/nonebot/nonebot2) 插件，制作头像相关的表情包\n\n### 使用\n\n发送“头像表情包”显示下图的列表：\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/lxgQ6tnoXNZECWj.jpg" width="400" />\n</div>\n\n\n每个表情包首次使用时会下载对应的图片和字体，可以手动下载 `resources` 下的 `images` 和 `fonts` 文件夹，放置于机器人运行目录下的 `data/petpet/` 文件夹中\n\n\n#### 触发方式\n- 指令 + @user，如： /爬 @小Q\n- 指令 + qq号，如：/爬 123456\n- 指令 + 自己，如：/爬 自己\n- 指令 + 图片，如：/爬 [图片]\n\n前三种触发方式会使用目标qq的头像作为图片\n\n#### 支持的指令\n\n- 摸\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/oNGVO4iuCk73g8S.gif" width="200" />\n</div>\n\n\n- 亲\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/RuoiqP8plJBgw9K.gif" width="200" />\n</div>\n\n\n- 贴/蹭\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/QDCE5YZIfroavub.gif" width="200" />\n</div>\n\n\n- 顶/玩\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/YwxA7fFgWyshuZX.gif" width="200" />\n</div>\n\n\n- 拍\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/5mv6pFJMNtzHhcl.gif" width="200" />\n</div>\n\n\n- 撕\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/DNIix6W1OmqknhU.jpg" width="200" />\n</div>\n\n\n- 丢\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/LlDrSGYdpcqEINu.jpg" width="200" />\n</div>\n\n\n- 爬\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/hfmAToDuF2actC1.jpg" width="200" />\n</div>\n\n\n- 精神支柱\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/WwjNmiz4JXbuE1B.jpg" width="200" />\n</div>\n\n\n- 一直\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/dAf9Z3kMDwYcRWv.gif" width="200" />\n</div>\n\n\n- 加载中\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/751Oudrah6gBsWe.gif" width="200" />\n</div>\n\n\n- 转\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/HoZaCcDIRgs784Y.gif" width="200" />\n</div>\n\n\n- 小天使\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/ZgD1WSMRxLIymCq.jpg" width="200" />\n</div>\n\n\n- 不要靠近\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/BTdkAzvhRDLOa3U.jpg" width="200" />\n</div>\n\n\n- 一样\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/SwAXoOgfdjP4ecE.jpg" width="200" />\n</div>\n\n\n- 滚\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/atzZsSE53UDIlOe.gif" width="200" />\n</div>\n\n\n- 玩游戏\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/Xx34I7nT8HjtfKi.png" width="200" />\n</div>\n\n\n- 膜\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/nPgBJwV5qDb1s9l.gif" width="200" />\n</div>\n\n\n- 吃\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/ba8cCtIWEvX9sS1.gif" width="200" />\n</div>\n\n\n- 啃\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/k82n76U4KoNwsr3.gif" width="200" />\n</div>\n\n\n- 出警\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/3OIxnSZymAfudw2.jpg" width="200" />\n</div>\n\n\n- 问问\n\n<div align="left">\n  <img src="https://s2.loli.net/2022/02/23/GUyax1BF6q5Hvin.jpg" width="200" />\n</div>\n',
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MeetWq/nonebot-plugin-petpet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
