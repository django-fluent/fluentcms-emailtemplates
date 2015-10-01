# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('slug', models.SlugField(help_text='This unique name can be used refer to this content in in code.', verbose_name='Internal name')),
                ('layout', models.CharField(default=b'default', max_length=100, verbose_name='Layout', choices=[(b'default', 'Default')])),
                ('sender_name', models.CharField(max_length=200, null=True, verbose_name='Sender name', blank=True)),
                ('sender_email', models.EmailField(max_length=75, null=True, verbose_name='Sender email', blank=True)),
                ('is_cross_site', models.BooleanField(default=False, help_text='This allows contents to be shared between multiple sites in this project.<br>\nMake sure that any URLs in the content work with all sites where the content is displayed.', verbose_name='Share between all sites')),
                ('parent_site', models.ForeignKey(default=10, editable=False, to='sites.Site')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Email template',
                'verbose_name_plural': 'Email templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplateTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('subject', models.CharField(help_text='Placeholders such as <code>{first_name}</code> can be used here.', max_length=255, verbose_name='Subject')),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='fluentcms_emailtemplates.EmailTemplate', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'fluentcms_emailtemplates_emailtemplate_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'Email template Translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplatetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplate',
            unique_together=set([('parent_site', 'slug')]),
        ),
    ]
