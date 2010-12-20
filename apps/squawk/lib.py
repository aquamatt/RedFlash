# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Utilities for managing the sending of messages via SMS and other channels
"""
import uuid
from django.conf import settings
from squawk import InvalidContactError
from squawk import InvalidGroupError
from squawk import InvalidEventError
from squawk import DisabledContactError
from squawk import DisabledGroupError
from squawk import DisabledEventError
from squawk import PartialSendError
from squawk.models import Contact
from squawk.models import ContactGroup
from squawk.models import AuditLog
from squawk.models import Event
from django.template import Context
from django.template import Template

GATEWAY = settings.GATEWAY()

def create_notification_id():
    return str(uuid.uuid4()).replace('-','')        
        
def message_contact(api_user, user_slug, message):
    """ Message a single contact. 
@todo some handling if GATEWAY is None or invalid
""" 
    notification_id = create_notification_id()
        
    try:
        contact = Contact.objects.get(slug = user_slug)
        if contact.enabled:
            GATEWAY.send(api_user, notification_id, 'contact', user_slug, [contact], message)
        else:
            raise DisabledContactError()
    except Contact.DoesNotExist:
        raise InvalidContactError("%s not found" % user_slug)
    
def message_group(api_user, group_slug, message):
    """ Message a group of contacts. 
@todo some handling if GATEWAY is None or invalid
@todo bare exception caught on GATEWAY.send: lazy
"""
    notification_id = create_notification_id()
    
    SEND_ERROR = None
    try:
        group = ContactGroup.objects.get(slug = group_slug)
        if not group.enabled:
            raise DisabledGroupError()
        contacts = [c for c in group.contacts.all() if c.enabled]
        try:
            GATEWAY.send(api_user, notification_id, 'group', group_slug, contacts, message)
        except Exception, ex:
            SEND_ERROR = ex
    except ContactGroup.DoesNotExist:
        raise InvalidGroupError("%s not found" % group_slug)
        
    if SEND_ERROR:
        raise PartialSendError("Error in sending message: %s" % SEND_ERROR)

def fire_event(api_user, event_slug, post_args):
    """ Fire an event and message associated users and groups. 
@todo inefficient double read of group/contact records - one in this loop
and one in the message_[contact|group] methods
@todo passed exceptions - PUT IN LOGGING, DAMNIT!"""
    notification_id = create_notification_id()
    
    try:
        event = Event.objects.get(slug = event_slug)
    except Event.DoesNotExist:
        raise InvalidEventError("%s not found" % event_slug)
    
    if not event.enabled:
        raise DisabledEventError()
    
    template = Template(event.message)
    context = Context(post_args)
    message = template.render(context)
    
    contacts = []
    for group in [g for g in event.groups.all() if g.enabled]:
        contacts += [c for c in group.contacts.all() if c.enabled]
    contacts += [c for c in event.contacts.all() if c.enabled]

    # de-dupe contacts in the list - order changes but we don't mind
    contacts = list(set(contacts))

    GATEWAY.send(api_user, notification_id, 'event', event_slug, contacts, message)
