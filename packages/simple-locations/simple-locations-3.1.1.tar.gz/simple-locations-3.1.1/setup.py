# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_locations',
 'simple_locations.management',
 'simple_locations.management.commands',
 'simple_locations.migrations']

package_data = \
{'': ['*'],
 'simple_locations': ['fixtures/*',
                      'locale/fr/LC_MESSAGES/*',
                      'static/css/*',
                      'static/images/*',
                      'static/javascripts/*',
                      'static/uni_form/*',
                      'templates/simple_locations/*',
                      'templates/simple_locations/admin/*']}

install_requires = \
['django-mptt>=0.13.4,<0.14.0']

setup_kwargs = {
    'name': 'simple-locations',
    'version': '3.1.1',
    'description': "The common location package for Catalpa's projects",
    'long_description': "## simple_locations\n\nThe common location package used for catalpa's projects. A hierarchical tree of geographical locations supporting location type and GIS data.\n\n## Admin\n\nThe admin site is set up to use Modeltranslations (if available in the parent app)\n\nFor modeltranslations, please remember to run `sync_translation_fields` in order to get `name_en`, `name_tet` etc. fields.\n\n\n## Environment\n\nThis is intended to be compatible with:\n - Django 3.1, 3.2, 4.0\n - Python 3.7, 3.8, 3.9\n\n```sh\ngh repo clone catalpainternational/simple_locations\npoetry install\n```\n\n### Changelog\n\n  * Version 3.1\n    - Added manage.py, test_settings, and wsgi to enable running simple_locations as a standalone project\n    - Updated code to match latest versions of `django-mptt` and django\n\n  * Version 3.0\n    - Code style changes (black, flake8) and\n\n  * Version 2.77\n    - first pass of updates for Python 3.8+ and Django 3.1+\n\n  * Version 2.75\n    - add modeltranslations\n\n  * Version 2.74\n    - fix CORS issue breaking maps in AreaAdmin\n    - typo in AreaChildrenInline\n\n  * Version 2.73\n    - add an inline showing children to the Area admin\n    - make the `geom` field optional\n\n  * Version 2.72\n    - optionally use django_extensions' ForeignKeyAutocompleteAdmin in admin interface\n\n\n#### Uploading a new version to PyPi\n\n\n* Create a new version with `poetry version [patch / minor / major]`\n* poetry build\n* poetry publish\n\nNote that if you need credentials contact one of the maintainers on pypi\n\n",
    'author': 'Joshua Brooks',
    'author_email': 'josh@catalpa.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/catalpainternational/simple_locations',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
