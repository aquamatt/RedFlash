# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'TransmissionLog.gateway_status'
        db.alter_column('squawk_transmissionlog', 'gateway_status', self.gf('django.db.models.fields.CharField')(max_length=400))

        # Changing field 'TransmissionLog.gateway_response'
        db.alter_column('squawk_transmissionlog', 'gateway_response', self.gf('django.db.models.fields.CharField')(max_length=400))


    def backwards(self, orm):
        
        # Changing field 'TransmissionLog.gateway_status'
        db.alter_column('squawk_transmissionlog', 'gateway_status', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'TransmissionLog.gateway_response'
        db.alter_column('squawk_transmissionlog', 'gateway_response', self.gf('django.db.models.fields.CharField')(max_length=40))


    models = {
        'squawk.apiuser': {
            'Meta': {'object_name': 'APIUser'},
            'api_key': ('django.db.models.fields.CharField', [], {'default': "'54c3a4ba32cfdc63dd72'", 'max_length': '20', 'db_index': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'squawk.contact': {
            'Meta': {'object_name': 'Contact'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'squawk.contactendpoint': {
            'Meta': {'object_name': 'ContactEndPoint'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['squawk.Contact']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_point': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'squawk.contactgroup': {
            'Meta': {'object_name': 'ContactGroup'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['squawk.Contact']", 'symmetrical': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'squawk.event': {
            'Meta': {'object_name': 'Event'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['squawk.Contact']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['squawk.ContactGroup']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'squawk.transmissionlog': {
            'Meta': {'object_name': 'TransmissionLog'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'api_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['squawk.APIUser']"}),
            'charge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['squawk.Contact']"}),
            'delivery_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_point': ('django.db.models.fields.IntegerField', [], {}),
            'enqueued': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gateway_response': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '400', 'blank': 'True'}),
            'gateway_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'notification_id': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'notification_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notification_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'send_ok': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['squawk']
