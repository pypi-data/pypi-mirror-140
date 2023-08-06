# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_gachalogs']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.20.0,<1.0.0',
 'matplotlib>=3.5.1',
 'nonebot-adapter-onebot>=2.0.0b1',
 'nonebot2>=2.0.0a14',
 'xlsxwriter>=3.0.2']

setup_kwargs = {
    'name': 'nonebot-plugin-gachalogs',
    'version': '0.1.3',
    'description': 'A Genshin GachaLogs analysis plugin for Nonebot2',
    'long_description': '<h1 align="center">Nonebot Plugin GachaLogs</h1></br>\n\n\n<p align="center">🤖 用于统计及导出原神祈愿记录的 Nonebot2 插件</p></br>\n\n\n<p align="center">\n  <a href="https://github.com/monsterxcn/nonebot-plugin-gachalogs/actions">\n    <img src="https://img.shields.io/github/workflow/status/monsterxcn/nonebot-plugin-gachalogs/Build%20distributions?style=flat-square" alt="actions">\n  </a>\n  <a href="https://raw.githubusercontent.com/monsterxcn/nonebot-plugin-gachalogs/master/LICENSE">\n    <img src="https://img.shields.io/github/license/monsterxcn/nonebot-plugin-gachalogs?style=flat-square" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-gachalogs">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-gachalogs?style=flat-square" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue?style=flat-square" alt="python"><br />\n</p></br>\n\n\n**安装方法**\n\n\n使用以下命令安装插件本体 ~~（插件暂未发布于 PyPI）~~：\n\n\n```bash\n# 从 Git 安装\ngit clone https://github.com/monsterxcn/nonebot-plugin-gachalogs.git\ncd nonebot_plugin_gachalogs\ncp -r nonebot_plugin_gachalogs /path/to/nonebot/plugins/\ncp -r resources/gachalogs /path/to/resources/\n```\n\n\n然后检查一下，别忘了安装依赖 `matplotlib` `Pillow` `xlsxwriter`！\n\n\n```bash\npython3 -m pip install matplotlib Pillow xlsxwriter\n```\n\n\n<details><summary><i>从 PyPI 安装</i></summary></br>\n\n\n```bash\n# 从 PyPI 安装\npython3 -m pip install nonebot-plugin-gachalogs\n```\n\n\n从 PyPI 安装后需要手动将 `resources/gachalogs` 文件夹内资源下载到服务端。\n\n\n</details>\n\n\n打开 Nonebot2 正在使用的 `.env` 文件，参考 [.env.example](.env.example) 添加以下配置：\n\n\n - `resources_dir` 包含 `gachalogs` 文件夹的上级目录路径\n - `gacha_expire_sec` 祈愿历史记录本地缓存过期秒数，不设置默认 1 小时\n - `cos_bucket_name` 腾讯云 COS 存储桶名称\n - `cos_bucket_region` 腾讯云 COS 存储桶地域\n - `cos_secret_id` 腾讯云 COS 存储桶 SecretId\n - `cos_secret_key` 腾讯云 COS 存储桶 SecretKey\n\n\n\\* *关于腾讯云 COS 的配置仅用于私聊导出文件*\n\n\n重启 Bot 即可体验此插件。\n\n\n**使用方法**\n\n\n插件支持以下命令：\n\n\n - `抽卡记录` / `ckjl`\n   \n   返回一张统计饼图，样式与 https://genshin.voderl.cn/ 一致。\n   \n   初次使用要求输入一次祈愿历史记录链接，只要回复的内容中含有即可，不必手动截取准确的链接地址。\n   \n   附带 `-f` / `--force` 可要求强制获取最新祈愿记录，祈愿记录结果默认缓存 1 小时。\n   \n   ![祈愿统计图](resources/readme/result.png)\n   \n - `抽卡记录导出` / `ckjldc`\n   \n   导出祈愿历史记录文件，可选格式包括 `.xlsx` 表格和 `.json` 文件，均符合 [统一可交换祈愿记录标准](https://github.com/DGP-Studio/Snap.Genshin/wiki/StandardFormat)（UIGF）格式。\n   \n   附带 `j` / `json` / `u` / `uigf` 可指定导出 `.json` 文件，否则默认导出 `.xlsx` 表格。\n   \n   管理员可使用 `ckjldc [qq] [format]` 格式命令导出指定 QQ 的祈愿历史记录。\n   \n   此功能需要配置腾讯云 COS 以实现私聊文件发送，创建的存储桶建议设为私有读写。\n   \n   ![导出示意图](resources/readme/export.png)\n\n\n**特别鸣谢**\n\n\n[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@sunfkny/genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) | [@voderl/genshin-gacha-analyzer](https://github.com/voderl/genshin-gacha-analyzer)\n\n\n> 插件主要功能是从 [@sunfkny/genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) 抄的，溜溜…\n',
    'author': 'monsterxcn',
    'author_email': 'monsterxcn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monsterxcn/nonebot-plugin-gachalogs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0',
}


setup(**setup_kwargs)
