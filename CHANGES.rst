Changelog
=========

Version 2.0 (2018-01-22)
------------------------

* Added Django 2.0 support.
* Dropped Django 1.6 / 1.7 / 1.8 / 1.9 support

Version 1.0 (2018-01-19)
------------------------

* Fixed Django 1.9 - 1.11 support.

Version 0.2.5 (2016-11-23)
--------------------------

* Fixed Python 3 import path.
* Fixed usage in a site with Wagtail settings context processor.

Version 0.2.4
-------------

* Fixed Django 1.9 errors

Version 0.2.3
-------------

* Added Django 1.7 migrations

Version 0.2.2
-------------

* Fixed packaging errors, omitted plain text templates

Version 0.2.1
-------------

* Fixed packaging errors, omitted HTML templates

Version 0.2
-----------

* Added ``EmailContentPlugin.render_replace_context_fields`` to replace context vars for custom plugins easily.
* Show missing fields as inline errors in the content.
* Improved string formatting options in text, allow ``{object.attr}`` in HTML text.
* Fixed HTML output after replacing absolute links.
* Fixed HTML entity escaping.
* Fixed unicode handling.
* Python 3 fixes


Version 0.1
-----------

* First public release

