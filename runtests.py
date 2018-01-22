#!/usr/bin/env python
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
from os import path

# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:',},
        },
        SITE_ID = 1,
        INSTALLED_APPS = (
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.auth',
            'fluent_contents',
            'fluentcms_emailtemplates',
            'fluentcms_emailtemplates.plugins.emailtext',
        ),
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': (),
                'OPTIONS': {
                    'loaders': (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ),
                    'context_processors': (
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django.contrib.auth.context_processors.auth',
                    ),
                },
            },
        ],
        MIDDLEWARE = (),
        TEST_RUNNER = 'django.test.runner.DiscoverRunner',
    )

DEFAULT_TEST_APPS = [
    'fluentcms_emailtemplates',
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ['test', '--traceback'] + other_args + test_apps
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
