# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" SMS gateway implementations
"""
import re
import urllib
import types

def _log(notification_id, gateway_response, api_user, notification_type, notification_slug, 
         contact, send_ok, message):
        # really really nasty hack because the gateway class is set in settings,
        # so the import fails as it is called before settings has fully instantiated
        # Better is to have the class in settings as  a String and sort out later
        from squawk.models import AuditLog
        ml = AuditLog(notification_id = notification_id,
                        gateway_response = gateway_response,
                        api_user = api_user,
                        notification_type = notification_type,
                        notification_slug = notification_slug,
                        contact = contact,
                        message = message,
                        send_ok = send_ok,
                        delivery_confirmed = False
                        )
        ml.save()

class DummyGateway(object):
    """ Dummy gateway for testing. """
    def __init__(self):
        self.LAST_MESSAGE = ""
        self.LAST_NOTIFICATION_ID = ""
        
    def send(self, api_user, 
             notification_id, notification_type, notification_slug, 
             contacts, message):
        """ Dummy gateway will raise Exception if message is "FAIL MESSAGE" or
return quietly otherwise. """
        self.LAST_MESSAGE = message
        self.LAST_NOTIFICATION_ID = notification_id
        
        send_ok = False if message == 'FAIL MESSAGE' else True
        
        for contact in contacts:
            _log(notification_id, 'xxx123', api_user, notification_type, 
                 notification_slug, contact, send_ok, message)    
            
        if not send_ok:            
            raise Exception("Send failed")

class ClickatellGateway(object):
    """ Gateway class for Clickatell: http://www.clickatell.com 
http://www.clickatell.com/downloads/http/Clickatell_HTTP.pdf

Clickatell has features such as escalating via alternate gateways if sending fails
after pre-determined time. It also allows you to check whether a message has been 
delivered. Even better you can specify a callback,
so if RedFlash is externally exposed we don't have to poll. Can then mark message 
delivery in log.   
"""
    SEND_OK_RE = re.compile("ID: ([a-z,0-9,A-Z]*)$")
    SEND_OK_MULTI_RE = re.compile("ID: ([a-z,0-9,A-Z]*) To: ([0-9]*)$")
    SEND_FAIL_RE = re.compile("ERR: (.*)$")
    SEND_FAIL_MULTI_RE = re.compile("ERR: (.*) To: ([0-9]*)$")

    def __init__(self):
        from django.conf import settings
        self.GATEWAY_USER = settings.GATEWAY_USER
        self.GATEWAY_PASSWORD = settings.GATEWAY_PASSWORD
        self.GATEWAY_API_ID = settings.GATEWAY_API_ID
        self.GATEWAY_URL = settings.GATEWAY_URL
        gon = getattr(settings, 'GATEWAY_ORIGIN_NUMBER', None)
        self.GATEWAY_ORIGIN_NUMBER = None
        if gon:
            self.GATEWAY_ORIGIN_NUMBER = re.sub('[+ ]', '', gon)
            
    def send(self, api_user, 
             notification_id, notification_type, notification_slug, 
             contacts, message):
        # extract numbers and index contacts by number as this will be needed
        # when processing response
        contacts_by_number = {}
        for contact in contacts:
            # here we're allowing for numbers to be input with easy-to-read
            # formatting for humans by cleansing at this point. Clickatel need
            # numbers in international format without '+' prefix. Multiple 
            # numbers to send to are comma delimited.     
            number = re.sub('[+ ]', '', contact.number.strip())
            contacts_by_number[number] = contact
        
        numbers = ",".join(contacts_by_number.keys())
        post_data = {'text':message,
                     'to':numbers,
                     'user':self.GATEWAY_USER,
                     'password':self.GATEWAY_PASSWORD,
                     'api_id':self.GATEWAY_API_ID,
                    }
        if self.GATEWAY_ORIGIN_NUMBER:
            post_data['from'] = self.GATEWAY_ORIGIN_NUMBER
            
        encoded_data = urllib.urlencode(post_data)
        
        u = urllib.urlopen(self.GATEWAY_URL,
                           data = encoded_data)
        has_error = None
        for line in u.readlines():
            OK_MO = self.SEND_OK_RE.match(line)
            OK_MULTI_MO = self.SEND_OK_MULTI_RE.match(line)
            NOK_MO = self.SEND_FAIL_RE.match(line)
            NOK_MULTI_MO = self.SEND_FAIL_MULTI_RE.match(line)
            
            if OK_MO: ## single number posting
                id = OK_MO.groups()[0]
                contact = contacts[0]
                _log(notification_id, id, api_user, notification_type, 
                     notification_slug, contact, True, message)
            
            elif OK_MULTI_MO: ## multiple numbers posting
                id, number = OK_MULTI_MO.groups()
                contact = contacts_by_number[number]
                _log(notification_id, id, api_user, notification_type, 
                     notification_slug, contact, True, message)

            elif NOK_MO: ## error single number
                err = NOK_MO.groups()[0]
                contact = contacts[0]
                _log(notification_id, err, api_user, notification_type, 
                     notification_slug, contact, False, message)
                has_error = err

            elif NOK_MULTI_MO: ## error multi number posting
                err, number = NOK_MULTI_MO.groups()
                contact = contacts_by_number[number]
                _log(notification_id, err, api_user, notification_type, 
                     notification_slug, contact, False, message)
                has_error = err
            else:
                # @todo log the error
                pass
    
            if has_error:
                raise Exception(has_error)