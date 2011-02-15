# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'AuditLog'
        db.delete_table('squawk_auditlog')

        # Adding model 'TransmissionLog'
        db.create_table('squawk_transmissionlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notification_id', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('gateway_response', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
            ('api_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.APIUser'])),
            ('notification_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('notification_slug', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.Contact'])),
            ('end_point', self.gf('django.db.models.fields.IntegerField')()),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('gateway_status', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('status_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('send_ok', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivery_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('charge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('squawk', ['TransmissionLog'])


    def backwards(self, orm):
        
        # Adding model 'AuditLog'
        db.create_table('squawk_auditlog', (
            ('notification_id', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('send_ok', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('gateway_status', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('status_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('notification_slug', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('notification_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('api_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.APIUser'])),
            ('delivery_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.Contact'])),
            ('gateway_response', self.gf('django.db.models.fields.CharField')(blank=True, max_length=40, db_index=True)),
            ('charge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('squawk', ['AuditLog'])

        # Deleting model 'TransmissionLog'
        db.delete_table('squawk_transmissionlog')


    models = {
        'squawk.apiuser': {
            'Meta': {'object_name': 'APIUser'},
            'api_key': ('django.db.models.fields.CharField', [], {'default': "'f7bcc6625a3ef2262254'", 'max_length': '20', 'db_index': 'True'}),
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
            'gateway_response': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'blank': 'True'}),
            'gateway_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
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
