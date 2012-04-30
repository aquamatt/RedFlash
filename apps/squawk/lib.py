# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Utilities for managing the sending of messages via SMS and other channels
"""
import squawk.gateway
import squawk.models
import uuid
from collections import defaultdict
from django.template import Context
from django.template import Template
from django.conf import settings
from squawk import DisabledContactError
from squawk import DisabledGroupError
from squawk import DisabledEventError
from squawk import InvalidContactError
from squawk import InvalidGroupError
from squawk import InvalidEventError
from squawk import PartialSendError
from squawk.models import Contact
from squawk.models import ContactGroup
from squawk.models import Event
from squawk.models import TransmissionLog
from squawk.tasks import transmit

def create_notification_id():
    return str(uuid.uuid4()).replace('-','')        

def enqueue(api_user, notification_id, notification_type, notification_slug, 
            contacts, message):
    """ Enqueue message(s) to a single contact endpoint """
    # group transmission logs according to endpoint
    endpoint_groups = defaultdict(list)
    for contact in contacts:
        if not contact.enabled:
            continue
        for ep in contact.contactendpoint_set.all():
            if not ep.enabled:
                continue
            tl = TransmissionLog(notification_id = notification_id,
                        gateway_response = '',
                        api_user = api_user,
                        notification_type = notification_type,
                        notification_slug = notification_slug,
                        contact = contact,
                        end_point = ep.end_point,
                        address = ep.address,
                        message = message,
                        enqueued = True,
                        send_ok = False,
                        delivery_confirmed = False,
                        gateway_status = '',
                        charge = None
                        )
            tl.save()
            endpoint_groups[ep.end_point].append(tl)

    # dispatch to gateways for each type of message
    
    if settings.SEND_IN_PROCESS:
        mthd = transmit
    else:
        mthd = transmit.delay

    # boolean refers to whether the endpoint batches output (True)- ie email has all 
    # addresses as BCC - or not (False) such as Twitter, where one API call per recipient
    # is required
    # @todo move this to somewhere else - settings maybe. Alternatively, do it in the gateway.
    # the twitter gateway could get called then itself cascade out the individual calls.

# @todo this sucks because some SMS end-points do not take bulk requests
    endpoints = dict([(squawk.models.SMS, True),
                      (squawk.models.TWITTER, False),
                      (squawk.models.EMAIL, True),
                      (squawk.models.WEBHOOK, False),
                     ])
    
    for ep in endpoint_groups.keys():
        batch = endpoints[ep]
        if batch:
            mthd([t.id for t in endpoint_groups[ep]], ep)
        else:
            [ mthd([x.id], ep) for x in endpoint_groups[ep] ] 


def message_contact(api_user, user_slug, message):
    """ Message a single contact. 
@todo some handling if GATEWAY is None or invalid
""" 
    notification_id = create_notification_id()
        
    try:
        contact = Contact.objects.get(slug = user_slug)
        if contact.enabled:
            enqueue(api_user, notification_id, 'contact', user_slug, [contact], message)
        else:
            raise DisabledContactError(
                message = "Contact '%s' (%s) is disabled" % (contact.name, user_slug))
    except Contact.DoesNotExist:
        raise InvalidContactError(message = "%s not found" % user_slug)

    return notification_id
    
def message_group(api_user, group_slug, message):
    """ Message a group of contacts. 
@todo some handling if GATEWAY is None or invalid
"""
    notification_id = create_notification_id()
    
    SEND_ERROR = None
    try:
        group = ContactGroup.objects.get(slug = group_slug)
        if not group.enabled:
            raise DisabledGroupError(message = "Group %s is disabled" % group.slug)
        contacts = [c for c in group.contacts.all() if c.enabled]
        try:
            enqueue(api_user, notification_id, 'group', group_slug, contacts, message)
        except Exception, ex:
            SEND_ERROR = ex
    except ContactGroup.DoesNotExist:
        raise InvalidGroupError(message = "%s not found" % group_slug)
        
    if SEND_ERROR:
        raise PartialSendError(message = "Error in sending message: %s" % SEND_ERROR,
                                notification_id = notification_id)

    return notification_id

def fire_event(api_user, event_slug, post_args):
    """ Fire an event and message associated users and groups. 
@todo inefficient double read of group/contact records - one in this loop
and one in the message_[contact|group] methods
@todo passed exceptions - PUT IN LOGGING, DAMNIT!
"""
    notification_id = create_notification_id()
    
    try:
        event = Event.objects.get(slug = event_slug)
    except Event.DoesNotExist:
        raise InvalidEventError(message = "%s not found" % event_slug)
    
    if not event.enabled:
        raise DisabledEventError(message = "Event %s is disabled" % event_slug)
    
    template = Template(event.message)
    context = Context(post_args)
    message = template.render(context)
    
    contacts = []
    for group in [g for g in event.groups.all() if g.enabled]:
        contacts += [c for c in group.contacts.all() if c.enabled]
    contacts += [c for c in event.contacts.all() if c.enabled]

    # de-dupe contacts in the list - order changes but we don't mind
    contacts = list(set(contacts))
    enqueue(api_user, notification_id, 'event', event_slug, contacts, message)

    return notification_id

def status_callback(callback_data):
    """ Receive POST with delivery status data from the gateway """
    squawk.gateway.gateway().status_callback(callback_data)
