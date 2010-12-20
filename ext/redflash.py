# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" RedFlash client library """
import urllib

class RedFlashClient(object):
    def __init__(self, rf_url, api_key):
        """ Create a client that connects to the specified RedFlash server
at rf_url using the api_key. """
        self.rf_url = rf_url
        self.api_key = api_key
        if not api_key:
            raise Exception("API KEY must be non-empty and not null")
        
    def _send(self, ctype, slug, data):
        data['api_key'] = self.api_key
        u = urllib.urlopen(self.rf_url+"/%s/%s/"%(ctype,slug), 
                    data = urllib.urlencode(data))
    
        return u
    
    def _notify(self, ctype, slug, message):
        """ Send message to a contact group or contact (specify in ctype) """
        data = {'message' : message}
        
        response = self._send(ctype, slug, data)    
        code = response.getcode()
        if code == 500:
            raise Exception("Server error: %s" % "".join(response.readlines()))
        elif code == 403:
            raise Exception("Invalid key")
        elif code == 404:
            raise Exception("Invalid or disabled recipient")
        
        return code
    
    def fire_event(self, slug, **data):
        """ Fire an event on the RedFlash server at rf_url """
        response = self._send('event', slug, data)
        code = response.getcode()
        if code == 500:
            raise Exception("Server error")
        elif code == 403:
            raise Exception("Invalid key")
        
        return code

    def notify_group(self, slug, message):
        """ Send message to a contact group """
        return self._notify('group', slug, message)
    
    def notify_contact(self, slug, message):
        """ Send message to a contact """
        return self._notify('contact', slug, message)
