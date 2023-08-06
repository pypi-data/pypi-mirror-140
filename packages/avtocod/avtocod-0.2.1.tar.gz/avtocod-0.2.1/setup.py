# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avtocod',
 'avtocod.methods',
 'avtocod.session',
 'avtocod.types',
 'avtocod.types.profile',
 'avtocod.types.review']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'pydantic>=1.8.2,<1.9.0']

setup_kwargs = {
    'name': 'avtocod',
    'version': '0.2.1',
    'description': 'Avtocod - неофициальный, элегантный, асинхронный враппер автокода',
    'long_description': '<p align="center">\n    <a href="https://github.com/Fom123/avtocod">\n        <img src="https://profi.avtocod.ru/img/icons/apple-touch-icon-152x152.png" alt="Avtocod" width="128">\n    </a>\n    <br>\n    <b>Avtocod - неофициальная Python библиотека</b>\n    <br>\n\n[![PyPI version](https://img.shields.io/pypi/v/avtocod.svg)](https://pypi.org/project/avtocod/)\n[![Code Quality Score](https://api.codiga.io/project/30917/score/svg)](https://frontend.code-inspector.com/public/project/30917/avtocod/dashboard)\n![Downloads](https://img.shields.io/pypi/dm/avtocod)\n![codecov](https://codecov.io/gh/Fom123/avtocod/branch/develop/graph/badge.svg)\n![mypy](https://img.shields.io/badge/type_checker-mypy-style=flat)\n</p>\n\n**Avtocod** - неофициальный, элегантный, асинхронный враппер [автокода](https://profi.avtocod.ru/).\nПозволяет взаимодействовать с апи автокода используя лишь данные от учетной записи.\n\n### Ключевые особенности\n- **Быстрый**\n- **Поддержка тайпхинтов**\n- **Асинхронный код**\n\n\n### Требования\n\n- Python 3.8 или выше.\n- [Аккаунт Автокода](https://profi.avtocod.ru/auth).\n\n\n### Установка\n\n``` bash\npip3 install -U avtocod\n```\n\n\n### Документация\n\nВременно, вместо документации, вы можете использовать [примеры](https://github.com/Fom123/avtocod/tree/main/examples)\n\n### Предупреждение\nОчень рекомендуется сменить ```User-Agent``` при работе с библиотекой.\nЭто можно сделать так:\n``` python\nfrom avtocod import AvtoCod\nfrom avtocod.session.aiohttp import AiohttpSession\n\nasync def main():\n    avtocod = AvtoCod(\n        session=AiohttpSession(\n            headers={"User-Agent": "your-user-agent-here"}\n        )\n    )\n```\nИли если вы используете конструктор:\n``` python\nfrom avtocod import AvtoCod\nfrom avtocod.session.aiohttp import AiohttpSession\n\nasync def main():\n    avtocod = await AvtoCod.from_credentials(\n        email="myuser@example.com",\n        password="mypassword",\n        session=AiohttpSession(\n            headers={"User-Agent": "your-user-agent-here"}\n        )\n    )\n```\n\n\n### Внесение своего вклада в проект\n\nЛюбой вклад в проект приветствуется.\n### Благодарности\n\n- [@JrooTJunior](https://github.com/JrooTJunior) за [Aiogram](https://github.com/aiogram/aiogram). Выбрал вас в качестве примера\n',
    'author': 'Fom123',
    'author_email': 'gamemode1.459@gmail.com',
    'maintainer': 'Fom123',
    'maintainer_email': 'gamemode1.459@gmail.com',
    'url': 'https://github.com/Fom123/avtocod',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
