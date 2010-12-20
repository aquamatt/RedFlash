# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" RedFlash client library """
import urllib

def fire_event(rf_url, slug, **data):
    """ Fire an event on the RedFlash server at rf_url """
    if 'api_key' not in data:
        raise Exception("You must supply an api_key")
    
    u = urllib.urlopen(rf_url+"/event/%s/"%slug, 
                data = urllib.urlencode(data))
    code = u.getcode()
    if code == 500:
        raise Exception("Server error")
    elif code == 403:
        raise Exception("Invalid key")
    
    return code

def _notify(rf_url, ctype, slug, api_key, message):
    """ Send message to a contact group or contact (specify in ctype) """
    if not api_key:
        raise Exception("You must supply an api_key")
    
    data = {'api_key' : api_key,
            'message' : message}
    
    u = urllib.urlopen(rf_url+"/%s/%s/"%(ctype,slug), 
                data = urllib.urlencode(data))
    code = u.getcode()
    if code == 500:
        raise Exception("Server error")
    elif code == 403:
        raise Exception("Invalid key")
    elif code == 404:
        raise Exception("Invalid or disabled recipient")
    
    return code


def notify_group(rf_url, slug, api_key, message):
    """ Send message to a contact group """
    return _notify(rf_url, 'group', slug, api_key, message)

def notify_contact(rf_url, slug, api_key, message):
    """ Send message to a contact """
    return _notify(rf_url, 'contact', slug, api_key, message)
