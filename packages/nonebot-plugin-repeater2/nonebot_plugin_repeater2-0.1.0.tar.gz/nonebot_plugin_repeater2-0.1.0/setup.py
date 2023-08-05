# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_repeater2']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0', 'nonebot2>=2.0.0-beta.2,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-repeater2',
    'version': '0.1.0',
    'description': 'Auto +1 in groups.',
    'long_description': '<div align="center">\n\n# Repeater\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_📻 复读机 📻_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot-plugin-repeater2/blob/main/LICENSE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0beta.2-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.1.0-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.1.0\n\n⚠ 适配nonebot2-2.0.0beta.2；\n\n## 安装\n\n1. 通过`pip`或`nb`安装，版本请指定`0.1.0`；\n\n2. 在原版基础上修改了配置，**默认所有群支持复读**，通过`REPEATER_OFF_GROUP`设置关闭的群：\n\n    ```python\n    REPEATER_OFF_GROUP=["123456789", "987654321"]\n    REPEATER_MINLEN=1 # 触发复读的文本消息最小长度（表情和图片无此限制）\n    ```\n\n## 功能\n\n当群里开始+1时，机器人也会参与其中。\n\n包括普通消息，QQ表情，还有图片（表情包）。\n\n## Fork from\n\n[ninthseason-nonebot-plugin-repeater](https://github.com/ninthseason/nonebot-plugin-repeater)',
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
