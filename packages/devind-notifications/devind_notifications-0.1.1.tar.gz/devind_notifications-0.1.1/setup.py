# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['devind_notifications',
 'devind_notifications.helpers',
 'devind_notifications.helpers.dispatch',
 'devind_notifications.migrations',
 'devind_notifications.models',
 'devind_notifications.permissions',
 'devind_notifications.schema',
 'devind_notifications.schema.mutations',
 'devind_notifications.schema.subscriptions',
 'devind_notifications.tasks']

package_data = \
{'': ['*'],
 'devind_notifications': ['management/seed/001.django_celery_beat/*']}

install_requires = \
['Django>=3,<4',
 'celery>=5.2.3,<6.0.0',
 'devind-core>=0.1.2,<0.2.0',
 'devind-helpers>=0.2.1,<0.3.0',
 'graphene-django>=2.15.0,<3.0.0']

setup_kwargs = {
    'name': 'devind-notifications',
    'version': '0.1.1',
    'description': 'Devind django app for notifications.',
    'long_description': None,
    'author': 'Victor',
    'author_email': 'lyferov@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/devind-team/devind-django-notifications',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
