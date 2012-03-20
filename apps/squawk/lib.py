# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Utilities for managing the sending of messages via SMS and other channels
"""
import squawk.gateway
import squawk.models
import uuid
from celery.task import task
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

def create_notification_id():
    return str(uuid.uuid4()).replace('-','')        

def enqueue(api_user, notification_id, notification_type, notification_slug, 
            contacts, message):
    """ Enqueue message(s) to a single contact endpoint """
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
    
    dequeue(notification_id) 

def dequeue(notification_id=None):
    """ Pull queued messages out and send them 
Normal use is to provide the notification_id (this is internal, RedFlash ID) but
for unit-tests you want to be able to say 'de-queue all' just in case code
architecture changes to dequeue out of process. To achieve this, set
notification_id to None. This mode should NOT be used unless testing as it
will result in messages going to the wrong people on a busy system (ie not
threadsafe)
"""

    query_keys = dict(enqueued = True)
    if notification_id:
        query_keys['notification_id'] = notification_id


    # Do each endpoint in turn as the gateway may batch them out, e.g. SMS can do
    # this
    sms_txlist = [t.id for t in 
            TransmissionLog.objects.filter(
            end_point = squawk.models.PHONE, **query_keys
            )]

    twitter_txlist = [t.id for t in 
            TransmissionLog.objects.filter(
            end_point = squawk.models.TWITTER, **query_keys
            )] 

    email_txlist = [t.id for t in 
            TransmissionLog.objects.filter(
            end_point = squawk.models.EMAIL, **query_keys
            )] 

    if settings.SEND_IN_PROCESS:
        mthd = transmit
    else:
        mthd = transmit.delay
    
    if sms_txlist:
        mthd(sms_txlist, "SMS")

    if twitter_txlist:
        for _id in twitter_txlist:
            mthd([_id,], "TWEET")

    if email_txlist:
        mthd(email_txlist, "EMAIL")


@task
def transmit(txids, method="SMS"):
    """ Destined to be run on a celery queue, txids is a list
of TransmissionLog IDs for the entries to be SMSed. or TWEETed 

method can take values SMS or TWEET
"""
    if method == "SMS":
        squawk.gateway.gateway().send(txids)
    elif method == "TWEET":
        squawk.gateway.twitter().send(txids)
    elif method == "EMAIL":
        squawk.gateway.email().send(txids)
    else:
        raise Exception("Unknown transmit method: %s" % method)

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
