## simple_locations

The common location package used for catalpa's projects. A hierarchical tree of geographical locations supporting location type and GIS data.

## Admin

The admin site is set up to use Modeltranslations (if available in the parent app)

For modeltranslations, please remember to run `sync_translation_fields` in order to get `name_en`, `name_tet` etc. fields.


## Environment

This is intended to be compatible with:
 - Django 3.1, 3.2, 4.0
 - Python 3.7, 3.8, 3.9

```sh
gh repo clone catalpainternational/simple_locations
poetry install
```

### Changelog

  * Version 3.1
    - Added manage.py, test_settings, and wsgi to enable running simple_locations as a standalone project
    - Updated code to match latest versions of `django-mptt` and django

  * Version 3.0
    - Code style changes (black, flake8) and

  * Version 2.77
    - first pass of updates for Python 3.8+ and Django 3.1+

  * Version 2.75
    - add modeltranslations

  * Version 2.74
    - fix CORS issue breaking maps in AreaAdmin
    - typo in AreaChildrenInline

  * Version 2.73
    - add an inline showing children to the Area admin
    - make the `geom` field optional

  * Version 2.72
    - optionally use django_extensions' ForeignKeyAutocompleteAdmin in admin interface


#### Uploading a new version to PyPi


* Create a new version with `poetry version [patch / minor / major]`
* poetry build
* poetry publish

Note that if you need credentials contact one of the maintainers on pypi

