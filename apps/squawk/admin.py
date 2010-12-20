from django.contrib import admin
from reversion.admin import VersionAdmin
from squawk.models import Contact
from squawk.models import ContactGroup
from squawk.models import APIUser
from squawk.models import Event
from squawk.models import MessageLog

class ContactAdmin(VersionAdmin):
    prepopulated_fields = {'slug': ("name",)}
    list_display = ('name', 'slug', 'number', 'enabled')
    fieldsets = (
        (None,
            {'fields':(
                ('name', 'slug', 'enabled'),
            )}
        ),
        ('Contact details',
            {'fields':(
                'number',
            )}
        ),
    )

class ContactGroupAdmin(VersionAdmin):
    prepopulated_fields = {'slug': ("name",)}
    list_display = ('name', 'slug', 'enabled')
    filter_horizontal = ['contacts',]
    fieldsets = (
        (None,
            {'fields':(
                ('name', 'slug', 'enabled'),
                'contacts',
            )}
        ),
    )

class APIUserAdmin(VersionAdmin):
    prepopulated_fields = {'slug': ("name",)}
    list_display = ('name', 'api_key', 'enabled', 'is_admin')
    fieldsets = (
        (None,
            {'fields':(
                ('name', 'slug', 'enabled', 'is_admin'),
                'api_key',
            )}
        ),
    )

class EventAdmin(VersionAdmin):
    prepopulated_fields = {'slug': ("name",)}
    list_display = ('name', 'slug', 'description', 'enabled')
    filter_horizontal = ['contacts','groups']
    fieldsets = (
        (None,
            {'fields':(
                ('name', 'slug', 'enabled'),
                'description',
                'message',
            )}
        ),
        ("Recipients",
            {'fields':(
                'contacts',
                'groups',
            )}
        )
    )

class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'notification_id', 'gateway_id', 'notification_type', 
                    'notification_slug', 'contact', 'message', 'has_error', 'delivery_confirmed')

    fieldsets = (
                 ( None,
                   { 'fields' : (
                                 ('notification_id', 'gateway_id'),
                                 ('api_user', 'contact'),
                                 ('notification_type','notification_slug'),
                                 'message',
                                 ('has_error','delivery_confirmed')
                                 )
                    }
                  ),
                 )

admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactGroup, ContactGroupAdmin)
admin.site.register(APIUser, APIUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(MessageLog, MessageLogAdmin)