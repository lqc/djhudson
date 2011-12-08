# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'FakeSouthModel.name'
        db.add_column('app_with_south_fakesouthmodel', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=128), keep_default=False)

    def backwards(self, orm):

        # Deleting field 'FakeSouthModel.name'
        db.delete_column('app_with_south_fakesouthmodel', 'name')

    models = {
        'app_with_south.fakesouthmodel': {
            'Meta': {'object_name': 'FakeSouthModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['app_with_south']
