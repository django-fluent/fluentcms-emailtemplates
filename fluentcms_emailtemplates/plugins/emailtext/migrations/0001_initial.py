# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_contents.extensions


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTextItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('html', fluent_contents.extensions.PluginHtmlField(help_text='Placeholders such as <code>{first_name}</code>, <code>{last_name}</code> and <code>{full_name}</code> can be used here.', verbose_name='Text')),
                ('text', models.TextField(help_text='If left empty, the HTML contents will be used to generate a plain-text version.', null=True, verbose_name='Plain text version', blank=True)),
            ],
            options={
                'db_table': 'contentitem_emailtext_emailtextitem',
                'verbose_name': 'E-mail text',
                'verbose_name_plural': 'E-mail text',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
