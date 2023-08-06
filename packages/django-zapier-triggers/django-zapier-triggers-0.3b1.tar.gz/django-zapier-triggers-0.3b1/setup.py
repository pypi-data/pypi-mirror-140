# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zapier', 'zapier.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.2,<5.0', 'python-dateutil']

setup_kwargs = {
    'name': 'django-zapier-triggers',
    'version': '0.3b1',
    'description': 'Simple Django app for managing Zapier triggers.',
    'long_description': '# Django Zapier Triggers\n\nDjango app for managing Zapier trigger authentication\n\nThis app provides the minimal scaffolding required to support a Zapier\ntrigger in your application. Specifically it supports token-based\nauthentication for [polling\ntriggers](https://platform.zapier.com/docs/triggers#polling-trigger).\n\n### Version support\n\nThis app supports Django 3.2+ (`HttpResponse.headers`), and Python 3.8+\n(`:=` operator).\n\n## How does it work?\n\nThe app has a single model that stores an API token (UUID) against a\nUser. The token object has the concept of "scope" which is an array of\nstrings representing API triggers that are supported. In effect it uses\nthe token UUID for authentication, and the token scopes for\nauthorization.\n\nA trigger itself is just a view that returns some data in the prescribed\nZapier format - which in Python terms is a JSON-serializable list of dicts,\neach of which must contain an `id` attr:\n\n```python\n[\n    {"id": 1, "name": "Fred"},\n    { ... }\n]\n```\n\nFor simple scenarios where you want to return a queryset, there is a base\nCBV `PollingTriggerView` which you can subclass.\n\n\n## Installation\n\nInstall the package using pip / poetry\n\n```\npip install django-zapier-triggers\n```\n\n## Configuration\n\n1. Add the app to your `INSTALLED_APPS`\n\n```python\n# settings.py\nINSTALLED_APPS = [\n    ...,\n    zapier,\n]\n```\n\n2. Run migrations to add model tables\n\n```\n$ python manage.py migrate\n```\n\n3. Add a url for the Zapier auth check\n\n```python\n# urls.py\nurlpatterns = [\n    ...\n    path(\n        "zapier/auth-check/",\n        zapier.views.zapier_token_check,\n        name="zapier_auth_check",\n    ),\n]\n```\n\n4. Configure Zapier trigger (https://platform.zapier.com/docs/triggers)\n\nThis app supports the "API Key" auth model for Zapier apps\nhttps://platform.zapier.com/docs/apikey\n\nYou must configure your Zapier authentication to use API Key\nauthentication, and in the step "Configure a Test Request & Connection\nLabel" you should ensure that you are passing the API Key as a request\nheader called "X-Api-Token", and not in the URL.\n\nNB You will need to host your application somewhere that is visible on\nthe internet in order to confirm that the authentication works. `ngrok`\nis a good option to run the application locally.\n\n## Usage\n\nNow that you have authentication set up, you can create your triggers. A\npolling trigger is nothing more that a GET endpoint that supports the\ntoken authentication and that returns an ordered list of JSON objects.\nZapier itself handles deduplication of objects using the `id` property\nof each object that is returned - you can read more about deduplication\nhere - https://zapier.com/help/create/basics/data-deduplication-in-zaps\n\nThis package is responsible for the endpoint authentication - everything\nelse is up to you. You can use the `polling_trigger` view function\ndecorator to guard the functions that you set up as triggers. The\ndecorator takes a required string argument, which is a scope that must\nmatch the incoming `request.auth`. The decorator handles request\nauthentication, setting the `request.user` and `request.auth`\nproperties.\n\n```python\n# views.py\n@zapier.decorators.polling_trigger("new_books")\ndef new_books_trigger(request: HttpRequest) -> JsonResponse:\n    latest_id = request.auth.get_latest_id("new_books") or -1\n    books = Book.objects.filter(id__gt=latest_id).order_by("-id")[:25]\n    data = [{"id": book.id, "title": book.title} for book in books]\n    return JsonReponse(data)\n```\n',
    'author': 'YunoJuno',
    'author_email': 'code@yunojuno.com',
    'maintainer': 'YunoJuno',
    'maintainer_email': 'code@yunojuno.com',
    'url': 'https://github.com/yunojuno/django-zapier-trigger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
