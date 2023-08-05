# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_app_parameter',
 'django_app_parameter.management',
 'django_app_parameter.management.commands',
 'django_app_parameter.migrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-app-parameter',
    'version': '0.1.3',
    'description': "App-Parameter is a very simple Django app to save application's parameter in the database.",
    'long_description': '# Django-app-parameter\n\nApp-Parameter is a very simple Django app to save application\'s parameter in the database. Therefor those parameter can be updated by users at running. It can be used to store title of the website, e-mail of the mail expeditor and so on.\n\nDetailed documentation is in the "docs" directory.\n\n## Install\n\n    pip install django-app-parameter\n\n## Quick start\n\n1. Add "django_app_parameter" to your INSTALLED_APPS setting like this:\n\n    INSTALLED_APPS = [\n        ...\n        "django_app_parameter",\n    ]\n\nIf you want to have your global parameter available in template, activate the provided context processor:\n\n    TEMPLATES = [\n        ...\n        "OPTIONS": {\n            "context_processors": [\n                ...\n                "django_app_parameter.context_processors.add_global_parameter_context",\n            ],\n        },\n    ]\n\n2. Run ``python manage.py migrate`` to create the django_app_parameter table in models.\n\n3. Start the development server and visit http://127.0.0.1:8000/admin/\n   to create parameters (you\'ll need the Admin app enabled).\n\n## Usage\n\nUse admin interface to add parameters. You can access a parameter in your code use the "slug" field. It\'s built at first save with: slugify(self.name).upper().replace("-", "_"), examples:\n\n```\n    self.name     ==> self.slug()\n    blog title    ==> BLOG_TITLE\n    sender e-mail ==> SENDER_E_MAIL\n    ##weird@Na_me ==> WERIDNA_ME\n```\n\nSee [Django\'s slugify function](https://docs.djangoproject.com/fr/4.0/ref/utils/#django.utils.text.slugify) for more informations.\n\nYou can read parameter anywhere in your code:\n\n    from django_app_parameter.models import Parameter\n\n    def send_confirmation_email_view(request):\n        from = Parameter.objects.str("TEAM_EMAIL")\n        subject = "Alright!"\n        ...\n        send_email(...)\n\nYou can also access "global" parameters from every templates:\n\n    <head>\n        <title>{{ BLOG_TITLE }}</title>\n    </head>\n\n## Ideas which could come later (or not)\n\n* A migration process to keep a list of your parameters in a file and automatically add them in each environment\n* Shortcut to use Parameter.str(slug) (skip \'objects\' key word)\n* Check correctness of value on save\n* Management command to add a new parameter\n* modification history\n\n## Why Django-App-Parameter\n\nBecause I wanted to try to package a Django app and I used this one in most of my projects so it seemed a good idea.',
    'author': 'Swann',
    'author_email': 'swann.bouviermuller@gmail.com',
    'maintainer': 'Swann',
    'maintainer_email': 'swann.bouviermuller@gmail.com',
    'url': 'https://github.com/Swannbm/django-app-parameter',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
