# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['propan',
 'propan.annotations',
 'propan.brokers',
 'propan.brokers.adapter',
 'propan.brokers.model',
 'propan.config',
 'propan.db',
 'propan.db.workers',
 'propan.db.workers.implementation',
 'propan.db.workers.implementation.alchemy',
 'propan.db.workers.implementation.tortoise',
 'propan.db.workers.model',
 'propan.fetch',
 'propan.fetch.fetcher',
 'propan.fetch.fetcher.adapter',
 'propan.fetch.fetcher.model',
 'propan.fetch.proxy',
 'propan.fetch.proxy.adapter',
 'propan.fetch.proxy.model',
 'propan.fetch.user_agent',
 'propan.logger',
 'propan.logger.adapter',
 'propan.logger.model',
 'propan.supervisors']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'aio-pika>=6.8.0,<7.0.0',
 'aiohttp>=3.7.4.post0,<4.0.0',
 'loguru>0.5.3',
 'pydantic>=1.8.2,<2.0.0',
 'uvloop>=0.16.0,<0.17.0',
 'watchgod>=0.6,<0.7']

entry_points = \
{'console_scripts': ['propan = propan:run']}

setup_kwargs = {
    'name': 'propan',
    'version': '0.0.3.5',
    'description': 'Simple and fast framework to create message brokers based microservices',
    'long_description': 'Propan существует, чтобы максимально упростить для вас создание микросервисов вокруг брокеров сообщений (например, RabbitMQ)\n\nОсновные особенности:\n\n* **Окружение**: максимальное удоство для работы с настройками проекта.\n* **Скорость разработки**: один декоратор - один потребитель на очередь.\n* **Обработка входных параметров**: автоматическая сериализация сообщений из RabbitMQ в соответствии с аннотацией типов.\n* **Расширяемость**: возможность создавать собственные классы-реализации интерфейсов Propan.\n* **Инъекция зависимостей**: единый подход к работе с зависимостям во всем проекте.\n\n## Окружение\n\nPython 3.8+\n\n\n## Примеры\n\n### Создание проекта\n\n* Создайте проект с помощью `propan --start test_project`\n* Перейдите в директорию проекта `cd test_project`\n* Создайте `app/config/settings.py` с данными для подключения к RabbitMQ\n\n```Python\nRABBIT_HOST = "127.0.0.1"\nRABBIT_LOGIN = "guest"\nRABBIT_PASSWORD = "guest"\nRABBIT_VIRTUALHOST = "/"\n```\n\n* Настройки проекта также можно указывать в `app/config/config.yml` файле\n\n```yml\nRABBIT:\n    host: \'127.0.0.1\'\n    login: \'guest\'\n    password: \'guest\'\n    vhost: /\n```\n\nВ таком случае переменные из `.yml` файла будут транслированы в настройки в верхнем регистре\n* Данные поля для RabbitMQ автоматически используются как параметры по умолчанию\n\n```yml\nRabbit:\n    host: \'127.0.0.1\'\n```\nАналогичен\n```yml\nRABBIT_HOST: \'127.0.0.1\'\n```\n\nПроект также автоматически берет переменные из окружения при наличии совпадений в названии переменных из `.yml` файла\n* Таким образом приоритеты использования переменных в конфликтных ситуациях расставлены следующим образом: `environment` > `config.yml` > `settings.py`\n* При попытке обратиться к переменной, которой нет в настройках, propan выдаст warning и `None` в качестве значения\n* `.yml` файлы можно переключать при запуске с помощью флага `--config=prod.yml` или `-C prod.yml`\n    * в таком случае все используемые `.yml` файлы должны находиться в директории `app/config/`\n\n\n* После указания данных для подключения к RabbitMQ создадим коннектор в `app/dependencies.py`\n\n```Python\nimport asyncio\n\nfrom propan.config import settings\nfrom propan.brokers import RabbitAdapter\n\nqueue_adapter = RabbitAdapter(\n    host = settings.RABBIT_HOST,\n    login = settings.RABBIT_LOGIN,\n    password = settings.RABBIT_PASSWORD,\n    virtualhost = settings.RABBIT_VHOST,\n    max_consumers=settings.MAX_CONSUMERS,\n) # данные поля settings используются для инициализации по умолчанию\n```\nГлобальные найстроки используются во всех случаях, когда необходимо получить доступ к константам проекта (инициализируются, как указано выше, при старте приложения)\n\n```Python\nfrom propan.config import settings\n```\n\n`settings.MAX_CONSUMERS` указывается при запуске проекта с помощью флага `--workers=10` или `-W 10` (10-значение по умолчанию) и определяет допустимое количество одновременно обрабатываемых сообщений\n\n* После создания `queue_adapter` создадим `PropanApp` в `app/serve.py`\n\n```Python\nfrom propan.app import PropanApp\n\nfrom .dependencies import queue_adapter\n\n# broker по умолчанию - RabbitAdapter(logger=loguru)\napp = PropanApp(broker=queue_adapter)\n\n@app.handle(queue_name="test_queue")\nasync def base_handler(message):\n    print(message)\n```\n\n* Запуск проекта осуществляется с помощью команды `propan app.serve:app`\n    * `app.serve` - путь к файлу serve, а `app` - название экземпляра `PropanApp` в коде.\n    * Запуск по умолчанию: `propan app.serve:app -C config.yml -W 10`\n    * Используйте флаг `--reload` для запуска проекта в тестовом режиме с автоматической перезагрузкой при изменении файлов\n\n\n\n### Сериализация входных параметров\n\n* Так как входящие значения RabbitMQ представляют из себя строку, для сериализации входных параметров Propan использует аннотацию типов\n\n```Python\nfrom propan.app import PropanApp\n\nfrom .dependencies import queue_adapter\n\napp = PropanApp(\n    broker=queue_adapter,\n    apply_types=True\n)\n\n@app.handle(queue_name="test_queue")\nasync def base_handler(user_id: int):  # приведение входного значения к типу int\n    print(message)\n```\n\nИспользование глобальной опции `apply_types=True` включит сериализацию входных параметров для всех handler\'ов приложения\n\n* Для использования сериализации в отдельных handler\'ах необходимо использовать специальный декоратор `apply_types`\n\n```Python\nfrom propan.app import PropanApp\nfrom propan.annotations import apply_types\n\nfrom .dependencies import queue_adapter\n\napp = PropanApp(broker=queue_adapter)\n\n@app.handle(queue_name="test_queue")\n@apply_types\nasync def base_handler(user_id: int):\n    print(message)\n```\n\n* Замечания\n    * функция-handler всегда должна принимать на вход один аргумент\n\n* Для сериализации более сложных объектов возможно использование классов-оберток над `pydantic`\n\n```Python\nfrom typing import Optional\n\nfrom propan.app import PropanApp\nfrom propan.annotations import MessageModel\n\napp = PropanApp(\n    broker=queue_adapter,\n    apply_types=True\n)\n\nclass User(MessageModel):\n    username: str\n    user_id: Optional[int]\n\n@app.handle(queue_name="test_queue")\nasync def base_handler(user: User):\n    print(user)\n```\n\n\n### Логирование\n\nВсе классы Propan, выводящие служебную информацию требуют для этого любой экземпляр logger\'a, являющегося реализацией интерфейса `propan.logger.model.usecase.LoggerUsecase`.\nРекомендуется использовать экземпляр этого класса во всем проекте, инициализируя его в `app/dependencies.py`.\n\n```Python\nfrom propan.logger.adapter.loguru_usecase import LoguruAdapter\n# также можно использовать\nfrom propan.logger import loguru # является экземпляром LoguruAdapter\n\nlogger = LoguruAdapter()\nqueue_adapter = RabbitAdapter(\n    logger=logger\n)\n```\n\n* По умолчанию во всех классах Propan используется `propan.logger.adapter.empty.EmptyLogger`\n\nТакже возможно построение цепочки обработки logger\'ов путем использования в качестве экземпляра logger класса `propan.logger.LoggerSimpleComposition`\n\n```Python\nfrom propan.logger import LoggerSimpleComposition, loguru\n\nlogger = LoggerSimpleComposition(\n    loguru, loguru\n) # последовательнок применение двух логгеров loguru\n```\n\n* В таком случае logger\'ы будут применяться в том порядке, в котором они были переданы в конструктор\n\nВсе logger\'ы поддерживают декоратор `logger.catch`, который позволяет совершать какие-либо действия при возникновении ошибки в функции\n\n```Python\n@logger.catch\n@app.handle(queue_name="test_queue")\nasync def base_handler(user: str):\n    print(user)\n```\n\n\n### Дополнительно\n\nДля возвращения сообщения в очередь при возникновении ошибки c отслеживанием количества попыток повторной обработки используйте декоратор `broker.retry`\n\n```Python\n@app.broker.retry(queue_name="test_queue", try_number=3)\n@app.handle(queue_name="test_queue")\nasync def base_handler(user: str):\n    print(user)\n```\n\n* Замечания\n    * При превышении количества повторных попыток `broker` вызывает метод `error` своего экземпляра `logger`\'а, а сообщение извлекается из очереди\n    * По умолчанию количество попыток - 3, название очереди - обязательный аргумент\n\nВ таком случае также может быть полезным использование декоратора `ignore_exceprions`\n\n```Python\nfrom propan.logger import ignore_exceptions\n\nNOT_CATCH = (ValueError,)\n\n@app.broker.retry(queue_name="test_queue", try_number=3)\n@app.handle(queue_name="test_queue")\n@ignore_exceptions(logger, NOT_CATCH)\nasync def base_handler(user: str):\n    print(user)\n```\n\n* Ошибки из `NOT_CATCH` не будут передаваться дальше по стеку, а будут обработаны с помощью метода `error` переданного экземпляра `logger`\'а\n\n\n\nХудший вариант вашего приложения будет выглядеть следующим образом:\n\n```Python\nfrom propan.app import PropanApp\nfrom propan.annotations import apply_types\nfrom propan.logger import ignore_exceptions\n\nfrom .dependencies import queue_adapter, logger\n\napp = PropanApp(\n    broker=queue_adapter\n)\n\nNOT_CATCH = (ValueError,)\n\n@logger.catch\n@app.broker.retry(queue_name="test_queue", try_number=3)\n@app.handle(queue_name="test_queue")\n@ignore_exceptions(logger, NOT_CATCH)\n@apply_types\nasync def base_handler(user: str):\n    print(user)\n```\n\n# Удачи!\n',
    'author': 'PasNA6713',
    'author_email': 'diementros@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PasNA6713/Propan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.8,<4',
}


setup(**setup_kwargs)
