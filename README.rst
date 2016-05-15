fluentcms-emailtemplates
========================

An email template system, that uses django-fluent-contents_ blocks to define the e-mail templates.

Features:

* Multilingual content.
* Multisite support.
* Custom layouts (=Django templates).
* Custom context variables


Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install fluentcms-emailtemplates

First make sure the project is configured for django-fluent-contents_.

Then add the following settings::

    INSTALLED_APPS += (
        'fluentcms_emailtemplates',
        'fluentcms_emailtemplates.plugins.emailtext',
    )

    FLUENTCMS_EMAILTEMPLATES_PLUGINS = ( 
        'EmailTextPlugin',
    )

The database tables can be created afterwards::

    ./manage.py migrate


Configuration
-------------

The following settings are defined by default:

.. code-block:: python

    FLUENTCMS_EMAILTEMPLATES_LAYOUTS = (
        # A layout points to a template named:
        # fluentcms_emailtemplates/emails/{slug}/{layout}.html
        # fluentcms_emailtemplates/emails/{layout}.html
        ('default', _("Default")),
    )

    # Possible plugins to use in the email template.
    # By default, that is FLUENT_CONTENTS_PLACEHOLDER_CONFIG['email_templates']
    FLUENTCMS_EMAILTEMPLATES_PLUGINS = ( 
        'EmailTextPlugin',
    )

    # Add extras context data for an e-mail preview.
    FLUENTCMS_EMAILTEMPLATES_PREVIEW_CONTEXT = {}

    # Optionally allow developers to share email templates between all sites in a multisite setup.
    FLUENTCMS_EMAILTEMPLATES_ENABLE_CROSS_SITE = False

    # Enable multisite support by default
    FLUENTCMS_EMAILTEMPLATES_FILTER_SITE_ID = True


Usage
=====

Create email templates in the admin.
Use the following code to create an email:

.. code-block:: python

    from email.utils import formataddr
    from fluentcms_emailtemplates.models import *

    template = EmailTemplate.objects.get_for_slug('order-confirmation')
    email = template.get_email_message(
        base_url='http://example.org/',
        context={
            'order_number': "123-xy"
        },
        to=[
            formataddr(('You', 'you@example.org')),
        ],
    )

    email.send()


Contributing
------------

If you like this module, forked it, or would like to improve it, please let us know!
Pull requests are welcome too. :-)

.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
