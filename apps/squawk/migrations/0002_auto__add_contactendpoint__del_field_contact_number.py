# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ContactEndPoint'
        db.create_table('squawk_contactendpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('end_point', self.gf('django.db.models.fields.IntegerField')()),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.Contact'])),
        ))
        db.send_create_signal('squawk', ['ContactEndPoint'])

        # Deleting field 'Contact.number'
        db.delete_column('squawk_contact', 'number')


    def backwards(self, orm):
        
        # Deleting model 'ContactEndPoint'
        db.delete_table('squawk_contactendpoint')

        # User chose to not deal with backwards NULL issues for 'Contact.number'
        raise RuntimeError("Cannot reverse this migration. 'Contact.number' and its values cannot be restored.")


    models = {
        'squawk.apiuser': {
            'Meta': {'object_name': 'APIUser'},
            'api_key': ('django.db.models.fields.CharField', [], {'default': "'ab6648c442e2f1432a7b'", 'max_length': '20', 'db_index': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'squawk.auditlog': {
            'Meta': {'object_name': 'AuditLog'},
            'api_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['squawk.APIUser']"}),
            'charge': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['squawk.Contact']"}),
            'delivery_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        }
    }

    complete_apps = ['squawk']
