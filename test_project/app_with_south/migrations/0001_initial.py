# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FakeSouthModel'
        db.create_table('app_with_south_fakesouthmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('app_with_south', ['FakeSouthModel'])


    def backwards(self, orm):
        
        # Deleting model 'FakeSouthModel'
        db.delete_table('app_with_south_fakesouthmodel')


    models = {
        'app_with_south.fakesouthmodel': {
            'Meta': {'object_name': 'FakeSouthModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['app_with_south']
