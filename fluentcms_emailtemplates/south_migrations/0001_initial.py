# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailTemplateTranslation'
        db.create_table(u'fluentcms_emailtemplates_emailtemplate_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            (u'master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['fluentcms_emailtemplates.EmailTemplate'])),
        ))
        db.send_create_signal(u'fluentcms_emailtemplates', ['EmailTemplateTranslation'])

        # Adding unique constraint on 'EmailTemplateTranslation', fields ['language_code', u'master']
        db.create_unique(u'fluentcms_emailtemplates_emailtemplate_translation', ['language_code', u'master_id'])

        # Adding model 'EmailTemplate'
        db.create_table(u'fluentcms_emailtemplates_emailtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('layout', self.gf('django.db.models.fields.CharField')(default='default', max_length=100)),
            ('sender_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sender_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('parent_site', self.gf('django.db.models.fields.related.ForeignKey')(default=10, to=orm['sites.Site'])),
            ('is_cross_site', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'fluentcms_emailtemplates', ['EmailTemplate'])

        # Adding unique constraint on 'EmailTemplate', fields ['parent_site', 'slug']
        db.create_unique(u'fluentcms_emailtemplates_emailtemplate', ['parent_site_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'EmailTemplate', fields ['parent_site', 'slug']
        db.delete_unique(u'fluentcms_emailtemplates_emailtemplate', ['parent_site_id', 'slug'])

        # Removing unique constraint on 'EmailTemplateTranslation', fields ['language_code', u'master']
        db.delete_unique(u'fluentcms_emailtemplates_emailtemplate_translation', ['language_code', u'master_id'])

        # Deleting model 'EmailTemplateTranslation'
        db.delete_table(u'fluentcms_emailtemplates_emailtemplate_translation')

        # Deleting model 'EmailTemplate'
        db.delete_table(u'fluentcms_emailtemplates_emailtemplate')


    models = {
        u'fluentcms_emailtemplates.emailtemplate': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent_site', 'slug'),)", 'object_name': 'EmailTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_cross_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'layout': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent_site': ('django.db.models.fields.related.ForeignKey', [], {'default': '10', 'to': u"orm['sites.Site']"}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'fluentcms_emailtemplates.emailtemplatetranslation': {
            'Meta': {'unique_together': "[(u'language_code', u'master')]", 'object_name': 'EmailTemplateTranslation', 'db_table': "u'fluentcms_emailtemplates_emailtemplate_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            u'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['fluentcms_emailtemplates.EmailTemplate']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['fluentcms_emailtemplates']