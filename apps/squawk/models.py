# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

from django.db import models
from django.utils import simplejson
import random

class SerializableModel(object):
    def json(self):
        """ Create a JSON representation of this objects with the
fields named in the _SERIALIZED_FIELDS_ list. """
        repr = {}
        for f in self._SERIALIZED_FIELDS_:
            repr[f] = getattr(self, f)
        return simplejson.dumps(repr)

# Create your models here.
class Contact(models.Model, SerializableModel):
    """
    Model representing a single contact with a telephone number 
"""
    _SERIALIZED_FIELDS_ = ['name', 'slug', 'number']

    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 100)
    enabled = models.BooleanField(default = True)
    number = models.CharField(max_length=20, blank = False)

    def __unicode__(self):
        return self.name
        
class ContactGroup(models.Model, SerializableModel):
    """
    Model representing a group of contacts mapped to a single name
"""
    _SERIALIZED_FIELDS_ = ['name', 'slug', 'short_contacts']

    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 100)
    contacts = models.ManyToManyField(Contact)
    enabled = models.BooleanField(default = True)

    def __unicode__(self):
        return self.name

    def _get_short_contacts(self):
        return [c.slug for c in self.contacts.all()]

    short_contacts = property(_get_short_contacts)


class APIUser(models.Model):
    """
    Each API user is allocated a key which is mandatory when making calls to send
messages out. An API user may or may not, according to the allow_inspect boolean, be
permitted to query contact and contact group data.
"""
    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 100)
    api_key = models.CharField(max_length = 20, 
                               default = lambda:hex(random.getrandbits(80))[2:-1],
                               db_index = True
                              )
    enabled = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False, 
                                        help_text = "Permit GET requests to retrieve contact data")

    def __unicode__(self):
        return self.name

class Event(models.Model):
    """ Users and groups can be bound to an event such that systems can flag an event and
administrators of the RedFlash system can determine who gets messaged when a given event
is fired. De-coupling users/groups from the conditions being messaged provides useful logical
separation."""
    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 100)
    description = models.CharField(max_length = 200,
                                   help_text = "Definition of the conditions under which this should be fired")
    enabled = models.BooleanField(default = True)
    message = models.CharField(max_length = 300, 
                               help_text = 'Message to be sent to recipients when this event is fired')
    contacts = models.ManyToManyField(Contact,
                                      help_text = 'Contacts to message when event is fired',
                                      blank = True)
    groups = models.ManyToManyField(ContactGroup,
                                    help_text = 'Groups to message when event is fired',
                                    blank = True)

RECIPIENT_CHOICES = ( ('contact', 'Contact'),
                      ('group', 'Group'),
                      ('event', 'Event'),
                     )
class MessageLog(models.Model):
    """
    Log of all messages sent.
"""
    timestamp = models.DateTimeField(auto_now_add = True)
    notification_id = models.CharField(max_length = 40, help_text = "RedFlash generated ID")
    gateway_id = models.CharField(max_length = 40, blank = True)
    api_user = models.ForeignKey(APIUser, help_text = "API User used to send the message")
    notification_type = models.CharField(max_length = 10, choices = RECIPIENT_CHOICES)
    notification_slug = models.CharField(max_length = 100, help_text = "slug of the contact or group")
    contact = models.ForeignKey(Contact)
    message = models.TextField()
    has_error = models.BooleanField(default = False)
    delivery_confirmed = models.BooleanField(default = False)