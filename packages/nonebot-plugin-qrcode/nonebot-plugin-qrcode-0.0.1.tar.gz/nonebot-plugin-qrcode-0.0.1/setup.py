# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_qrcode']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18.0,<1.0.0',
 'nonebot-adapter-onebot>=2.0.0.beta.1,<3.0.0',
 'nonebot2>=2.0.0.beta.1,<3.0.0',
 'pillow>=8.3.1,<9.0.0',
 'pyzbar-x>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'nonebot-plugin-qrcode',
    'version': '0.0.1',
    'description': 'qq聊天二维码插件',
    'long_description': '# nonebot-plugin-qrcode\n\n- 本地识别二维码\n- 支持一图片多个二维码\n- 支持多图片\n\n# 下载&安装\n\n## 插件本体\n\n```bash\npip install -U nonebot-plugin-qrcode\n```\n\n## !!!必须要的库 `libzbar0`\n\n### docker / ubuntu 等使用 `apt` 的\n\n```\napt install -y libzbar0\n```\n\n### centos\n\n~~自己找或者 pr 文档~~\n\n# 使用\n\n以下默认你设置了 `COMMAND_START=""`\n\n- `qr`\n\n  - 如果指令后**有图片**，则直接识别图片\n  - 如果**没有图片**，则会询问图片\n\n- `pqr`\n  - 识别聊天中，上一条图片消息中的二维码\n\n# 有疑问\n\n- ~~自己想~~\n- pr 或 issue\n',
    'author': 'kexue',
    'author_email': 'x@kexue.io.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kexue-z/nonebot-plugin-qrcode',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
