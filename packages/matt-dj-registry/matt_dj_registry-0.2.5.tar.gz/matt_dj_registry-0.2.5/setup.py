# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['registry', 'registry.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3,<4']

setup_kwargs = {
    'name': 'matt-dj-registry',
    'version': '0.2.5',
    'description': 'A simple, easy access key-value registry for Django.',
    'long_description': '# DJ-Registry\nThis is a simple, easy access key-value registry for Django. Sometimes you would like to have some flexibility in your settings.\nPutting your settings in `settings.py` or as environment variables also mean an engineer familiar with code or command line is required to alter them.\n\nThis Django app leverage the built-in Django admin so changing settings is easier as you can use the web interface.\n\n## Requirements\n* Python = "^3.6"\n* Django = "^3"\n\nRun the following command inside project\'s root folder to install it\'s dependencies with Poetry:\n\n```\n$ poetry install\n```\nYou can specify to the command that you do not want the development dependencies installed by passing the `--no-dev` option.\n\nIf you have not yet installed Poetry, please refer to their [official documentation](https://python-poetry.org/docs/#installation).\n\n## Installation\n\nInstall DJ-Registry with your favorite Python package manager:\n\n```\n(venv)$ pip install dj_registry\n```\n\nAdd `registry` to your `INSTALLED_APPS` settings:\n\n```py\nINSTALLED_APPS = [\n    # other apps...\n\n    \'registry\',\n]\n```\n\nMigrate the database\n\n```\n(venv)$ ./manage.py migrate\n```\n\nThen, we\'re all set!\n\n## Usage\n\nLog in to the admin, and create some keys under the **Django Registry** > **Entries** section. Let\'s say, we create `mailgun.key` and `mailgun.domain` with the corresponding `string` type and values.\nWe then create another entry with `game.max_score` as the key, `10000` as the value and `integer` as the type.\n\nThe following example shows you how to access them in code:\n\n```py\nfrom registry.helper import reg\n\nkey = reg[\'mailgun.key\']            # the key that you set\ndomain = reg[\'mailgun.domain\']      # the domain that you set\n\nmax_score = reg[\'game.max_score\']   # 10000, it is returned as an int\n```\n\nYou can also use `get` if you want to have a default and avoid exceptions if the key is not available (not enabled or does not exist)\n\n```py\nreg.get(\'game.levels\', 10)          # return 10 if key not found or disabled\nreg[\'game.levels\']                  # KeyError if key not found or disabled\n```\n\nYou can set or delete entry if you want\n```py\nreg[\'game.levels\'] = 12             # Set game.levels to 12 (integer) and save\ndel reg[\'game.levels\']              # Delete game.levels\n```\n\n## Enabled and comment field\nIf you want to disable a key, just toggle the `enabled` boolean in the admin interface. It would be treated as if the key didn\'t exist. This is something meant to be used in the admin interface.\nIf you want to manipulate this in the code, you will have to access the raw model like the following:\n\n```py\nfrom registry.models import Entry\n\ne = Entry.objects.get(\'game.levels\')\ne.enabled = False\ne.save()\n```\n\nThe comment field is also meant to be used in the admin interface. It is a convenient cell for user to put comments regarding to the settings, something like the following:\n\n```\n50: average use case.\n9999: maximum special case\n```\n\n## Types\n`integer`, `float`, `string`, and `boolean` are the supported types for now.\n',
    'author': 'Matt.Wang',
    'author_email': 'mattwang44@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mattwang44/dj-registry',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
