# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Contact'
        db.create_table('squawk_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('squawk', ['Contact'])

        # Adding model 'ContactGroup'
        db.create_table('squawk_contactgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('squawk', ['ContactGroup'])

        # Adding M2M table for field contacts on 'ContactGroup'
        db.create_table('squawk_contactgroup_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactgroup', models.ForeignKey(orm['squawk.contactgroup'], null=False)),
            ('contact', models.ForeignKey(orm['squawk.contact'], null=False))
        ))
        db.create_unique('squawk_contactgroup_contacts', ['contactgroup_id', 'contact_id'])

        # Adding model 'APIUser'
        db.create_table('squawk_apiuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(default='ccf4b1707452afebeb72', max_length=20, db_index=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('squawk', ['APIUser'])

        # Adding model 'Event'
        db.create_table('squawk_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('squawk', ['Event'])

        # Adding M2M table for field contacts on 'Event'
        db.create_table('squawk_event_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['squawk.event'], null=False)),
            ('contact', models.ForeignKey(orm['squawk.contact'], null=False))
        ))
        db.create_unique('squawk_event_contacts', ['event_id', 'contact_id'])

        # Adding M2M table for field groups on 'Event'
        db.create_table('squawk_event_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['squawk.event'], null=False)),
            ('contactgroup', models.ForeignKey(orm['squawk.contactgroup'], null=False))
        ))
        db.create_unique('squawk_event_groups', ['event_id', 'contactgroup_id'])

        # Adding model 'AuditLog'
        db.create_table('squawk_auditlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notification_id', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('gateway_response', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, blank=True)),
            ('api_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.APIUser'])),
            ('notification_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('notification_slug', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['squawk.Contact'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('gateway_status', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('status_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('send_ok', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivery_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('charge', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('squawk', ['AuditLog'])


    def backwards(self, orm):
        
        # Deleting model 'Contact'
        db.delete_table('squawk_contact')

        # Deleting model 'ContactGroup'
        db.delete_table('squawk_contactgroup')

        # Removing M2M table for field contacts on 'ContactGroup'
        db.delete_table('squawk_contactgroup_contacts')

        # Deleting model 'APIUser'
        db.delete_table('squawk_apiuser')

        # Deleting model 'Event'
        db.delete_table('squawk_event')

        # Removing M2M table for field contacts on 'Event'
        db.delete_table('squawk_event_contacts')

        # Removing M2M table for field groups on 'Event'
        db.delete_table('squawk_event_groups')

        # Deleting model 'AuditLog'
        db.delete_table('squawk_auditlog')


    models = {
        'squawk.apiuser': {
            'Meta': {'object_name': 'APIUser'},
            'api_key': ('django.db.models.fields.CharField', [], {'default': "'3a8cca6f311c246f27f9'", 'max_length': '20', 'db_index': 'True'}),
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
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
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
