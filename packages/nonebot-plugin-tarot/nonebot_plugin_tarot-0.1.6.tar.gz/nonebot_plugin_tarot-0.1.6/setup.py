# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_tarot']

package_data = \
{'': ['*'], 'nonebot_plugin_tarot': ['resource/*']}

install_requires = \
['nonebot-adapter-cqhttp==2.0.0-alpha.16', 'nonebot2==2.0.0-alpha.16']

setup_kwargs = {
    'name': 'nonebot-plugin-tarot',
    'version': '0.1.6',
    'description': 'Tarot divination for everyday!',
    'long_description': '<div align="center">\n\n# Tarot\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🔮 塔罗牌 🔮_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot_plugin_tarot/blob/alpha/LICENSE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0alpha.16-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.1.6-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.1.6\n\n⚠ 适配nonebot2-2.0.0alpha.16；\n\n👉 适配nonebot-2.0.0beta.1版本参见[beta.1分支](https://github.com/KafCoppelia/nonebot_plugin_tarot/tree/beta.1)\n\n[更新日志](https://github.com/KafCoppelia/nonebot_plugin_tarot/releases/tag/v0.1.6)\n\n## 安装\n\n1. 通过`pip`或`nb`安装，版本请指定`0.1.6`；\n\n2. 塔罗牌图片资源默认位于`./resource`下，设置`env`下`TAROT_PATH`更改资源路径，`CHAIN_REPLY`设置启用转发模式；\n\n3. 占卜一下你的今日运势！🥳\n\n## 功能\n\n1. 塔罗牌！占卜今日运势；\n\n2. 支持群聊/私聊占卜；\n\n3. 支持单张/全套塔罗牌占卜；\n\n4. **新增** 插件帮助文案；\n\n## 命令\n\n1. 占卜：占卜4张塔罗牌；\n\n2. 塔罗牌：得到单张塔罗牌回应；\n\n## 本插件改自\n\n1. [真寻bot插件库-tarot](https://github.com/AkashiCoin/nonebot_plugins_zhenxun_bot)\n\n2. [HoshinoBot-tarot](https://github.com/haha114514/tarot_hoshino)\n',
    'author': 'KafCoppelia',
    'author_email': 'k740677208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
