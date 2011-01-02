# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

from django.http import HttpResponse
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
from squawk.models import APIUser
from squawk.models import Contact
from squawk.models import ContactGroup

def contact_request(request, slug=None):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse("You must specify your API key", status = 500)
            
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse("Invalid API key for operation", status = 403)

    if request.method == 'POST':
        message = request.POST.get('message', None)
        if not message:
            response = HttpResponse("Empty message", status = 500)
        else:
            try:
                message_contact(api_user, slug, message)
                response = HttpResponse("Message sent", status = 201)
            except InvalidContactError:
                response = HttpResponse("Invalid contact", status = 404)
            except DisabledContactError:
                response = HttpResponse("Disabled contact", status = 404)
            except Exception, ex:
                response = HttpResponse("Error: %s" % ex, status = 500)
                
    elif request.method == 'GET':
        if not api_user.is_admin:
            return HttpResponse("Insufficient privileges", status = 403)
        
        try:
            contact = Contact.objects.get(slug=slug)
            if contact.enabled:
                response = HttpResponse(contact.json(), status = 200)
            else:
                response = HttpResponse("Disabled user", status = 404)
        except Contact.DoesNotExist:
            return HttpResponse("Invalid contact: %s" % slug, status = 404)
                
    else:
        response = HttpResponse("Invalid request method", status = 403)

    return response

def group_request(request, slug=None):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse("You must specify your API key", status = 500)
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse("Invalid API key for operation", status = 403)
      
    if request.method == 'POST':
        message = request.POST.get('message', None)
        if not message:
            response = HttpResponse("Empty message", status = 500)
        else:
            try:
                message_group(api_user, slug, message)
                response = HttpResponse("Message sent", status = 201)
            except InvalidGroupError:
                response = HttpResponse("Invalid group", status = 404)
            except DisabledGroupError:
                response = HttpResponse("Disabled group", status = 404)
            except PartialSendError, pse:
                response = HttpResponse("Could not send to some members of %s: %s" %(slug, pse), 
                                        status = 202)
            except Exception, ex:
                response = HttpResponse("Error: %s" % ex, status = 500)

    elif request.method == 'GET':
        if not api_user.is_admin:
            return HttpResponse("Insufficient privileges", status = 403)
        
        try:
            group = ContactGroup.objects.get(slug=slug)
            if group.enabled:
                response = HttpResponse(group.json(), status = 200)
            else:
                response = HttpResponse("Disabled group", status = 404)
        except ContactGroup.DoesNotExist:
            return HttpResponse("Invalid group: %s" % slug, status = 404)

    else:
        response = HttpResponse("Invalid request method", status = 403)

    return response

def event_request(request, slug):
    api_key = request.REQUEST.get('api_key', None)
    if not api_key:
        return HttpResponse("You must specify your API key", status = 500)
    try:
        api_user = APIUser.objects.get(api_key = api_key)
    except APIUser.DoesNotExist:
        return HttpResponse("Invalid API key for operation", status = 403)

    if request.method == 'POST':
        try:
            fire_event(api_user, slug, request.POST)
            response = HttpResponse("Event fired", status = 201)
        except InvalidEventError:
            response = HttpResponse("Invalid event", status = 404)
        except DisabledEventError:
            response = HttpResponse("Disabled event", status = 404)
        except Exception, ex:
            response = HttpResponse("Error: %s" % ex, status = 500)

    else:
        response = HttpResponse("Invalid request method", status = 403)

    return response

def delivery_status(request):
    """ Handler for delivery status callbacks from gateway. Expects a POST 
submission. """
    status_callback(request.POST)
    return HttpResponse("OK", status = 200)
    