# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['request_logger',
 'request_logger.management',
 'request_logger.management.commands',
 'request_logger.migrations']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.0,<5.0']

setup_kwargs = {
    'name': 'django-request-logger-2',
    'version': '0.3.1',
    'description': 'Django model for storing HttpRequest information.',
    'long_description': '# Django Request Log\n\nSimple Django model for logging HttpRequest instances.\n\n## Why?\n\nWe have a number of libraries that store elements of a request (path,\nquerystring, user, response code, remote_addr, and so on), and it seemed\nlike time to create a single model that we can use in all of them,\nstoring a common set of values.\n\nThis is not a replacement for web server logs - it\'s a utility for use\nin specific situations where you want to accurately log that someone\nrequested something.\n\n## How it works\n\nThere is a single model, `RequestLog` and a model manager with a\n`create` method that can take in a standard `HttpRequest` and / or\n`HttpResponse` object and create a new `RequestLog` object. If you\nare using this to record view functions, there is also a decorator,\n`log_request` that will take care of all this for you:\n\n```python\nfrom request_logger.decorators import log_request\n\n@log_request("downloads")\ndef download(request: HttpRequest) -> HttpReponse:\n    return HttpResponse("OK")\n    \n\n@log_request(lambda r: r.user.get_full_name())\ndef download(request: HttpRequest) -> HttpReponse:\n    return HttpResponse("OK")\n```\n\nThe `log_request` argument is mandatory and is used as a "reference",\nor category classifier. It can be a str, or a callable which takes\nin the request as a single arg.\n\n## Screenshots\n\n**Admin list view**\n\n<img src="screenshots/admin-list.png">\n\n**Admin item view**\n\n<img src="screenshots/admin-edit.png">\n',
    'author': 'YunoJuno',
    'author_email': 'code@yunojuno.com',
    'maintainer': 'YunoJuno',
    'maintainer_email': 'code@yunojuno.com',
    'url': 'https://github.com/yunojuno/django-request-log',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
