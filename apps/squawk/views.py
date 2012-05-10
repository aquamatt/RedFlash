# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
import logging

from django.http import HttpResponse
from django.conf import settings
from squawk import InvalidContactError
from squawk import InvalidGroupError
from squawk import InvalidEventError
from squawk import DisabledContactError
from squawk import DisabledGroupError
from squawk import DisabledEventError
from squawk import PartialSendError
from squawk.lib import message_contact
from squawk.lib import message_group
from squawk.lib import fire_event
from squawk.lib import status_callback
from squawk.lib import inbound_callback
from squawk.models import APIUser
from squawk.models import Contact
from squawk.models import ContactGroup

def contact_request(request, slug=None):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse('{"message": "You must specify your API key"}', 
                            content_type="application/json", status = 500)
            
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse('{"message": "Invalid API key for operation"}', 
                            content_type="application/json", status = 403)

    if request.method == 'POST':
        message = request.POST.get('message', None)
        if not message:
            response = HttpResponse('{"message": "Empty message"}', 
                            content_type="application/json", status = 500)
        else:
            try:
                nid = message_contact(api_user, slug, message)
                response = HttpResponse('{"message": "OK", "notification_id": "%s"}'%nid, 
                            content_type="application/json", status = 201)
            except InvalidContactError, ice:
                response = HttpResponse(ice.message, status = 404)
            except DisabledContactError, dce:
                response = HttpResponse(dce.message, status = 404)
            except Exception, ex:
                response = HttpResponse('{"message": "%s"}' % str(ex), 
                            content_type="application/json", status = 500)
                
    elif request.method == 'GET':
        if not api_user.is_admin:
            return HttpResponse('{"message": "Insufficient privileges"}', 
                        content_type="application/json", status = 403)
        
        try:
            contact = Contact.objects.get(slug=slug)
            if contact.enabled:
                response = HttpResponse(contact.json(), 
                        content_type="application/json", status = 200)
            else:
                response = HttpResponse('{"message": "Disabled user"}', 
                            content_type="application/json", status = 404)
        except Contact.DoesNotExist:
            return HttpResponse('{"message": "Invalid contact: %s"}' % slug, 
                        content_type="application/json", status = 404)
            
    else:
        response = HttpResponse('{"message": "Invalid request method"}', 
                            content_type="application/json", status = 403)

    return response

def group_request(request, slug=None):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse('{"message": "You must specify your API key"}', 
                            content_type="application/json", status = 500)
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse('{"message": "Invalid API key for operation"}', 
                            content_type="application/json", status = 403)
      
    if request.method == 'POST':
        message = request.POST.get('message', None)
        if not message:
            response = HttpResponse('{"message": "Empty message"}', 
                        content_type="application/json", status = 500)
        else:
            try:
                nid = message_group(api_user, slug, message)
                response = HttpResponse('{"message": "OK", "notification_id": "%s"}'%nid, 
                            content_type="application/json", status = 201)
            except InvalidGroupError, ige:
                response = HttpResponse(ige.message, status = 404)
            except DisabledGroupError, dge:
                response = HttpResponse(dge.message, status = 404)
            except PartialSendError, pse:
                response = HttpResponse(pse.message, status = 202)
            except Exception, ex:
                response = HttpResponse('{"message": "%s"}' % str(ex), 
                            content_type="application/json", status = 500)

    elif request.method == 'GET':
        if not api_user.is_admin:
            return HttpResponse('{"message": "Insufficient privileges"}', 
                        content_type="application/json", status = 403)
        
        try:
            group = ContactGroup.objects.get(slug=slug)
            if group.enabled:
                response = HttpResponse(group.json(), 
                       content_type="application/json", status = 200)
            else:
                response = HttpResponse('{"message": "Disabled group"}', 
                                content_type="application/json", status = 404)
        except ContactGroup.DoesNotExist:
            return HttpResponse('{"message": "Invalid group: %s"}' % slug, 
                            content_type="application/json", status = 404)

    else:
        response = HttpResponse('{"message": "Invalid request method"}', 
                            content_type="application/json", status = 403)

    return response

def event_request(request, slug):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse('{"message": "You must specify your API key"}', 
                        content_type="application/json", status = 500)
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse('{"message": "Invalid API key for operation"}', 
                            content_type="application/json", status = 403)

    if request.method == 'POST':
        try:
            nid = fire_event(api_user, slug, request.POST)
            response = HttpResponse('{"message": "OK", "notification_id": "%s"}'%nid,
                            content_type="application/json", status = 201)
        except InvalidEventError, iee:
            response = HttpResponse(iee.message, status = 404)
        except DisabledEventError, dee:
            response = HttpResponse(dee.message, status = 404)
        except Exception, ex:
            response = HttpResponse('{"message": "%s"}' % str(ex), 
                            content_type="application/json", status = 500)
    else:
        response = HttpResponse('{"message": "Invalid request method"}', 
                            content_type="application/json", status = 403)

    return response

def delivery_status(request):
    """ Handler for delivery status callbacks from gateway. 
"""
    callback_method = getattr(settings, 'GATEWAY_CALLBACK_METHOD', 'POST').upper()
    if callback_method not in ['GET', 'POST']:
        callback_method = 'POST'
    status_callback(getattr(request, callback_method))
    return HttpResponse("OK", status = 200)

def inbound_message(request):
    """ Handler for INBOUND messages from the SMS gateway. If a message 
arrives but the gateway class doesn't support it, a 200 will be returned 
regardless (to prevent endless re-sends by the gateway) and an error will
be logged. Response body is OK if handled, DISCARDED if not. """
    logger = logging.getLogger("redflash")
    callback_method = getattr(settings, 'GATEWAY_CALLBACK_METHOD', 'POST')
    MSG = "OK"
    if callback_method not in ['GET', 'POST']:
        callback_method = 'POST'
    try:
        inbound_callback(getattr(request, callback_method))
    except NotImplementedError, nie:
        logger.error("Inbound message not handled by gateway handler")
        MSG = "DISCARDED"
    except Exception, ex:
        logger.error("Inbound message handling error: %s" % str(ex))
        MSG = "DISCARDED"
    return HttpResponse(MSG, status = 200)
    
