# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" SMS gateway implementations
"""
import re
import squawk
import urllib
from datetime import datetime
from django.conf import settings
from squawk.models import TransmissionLog

class ClickatellGateway(object):
    """ Gateway class for Clickatell: http://www.clickatell.com 
http://www.clickatell.com/downloads/http/Clickatell_HTTP.pdf

Clickatell has features such as escalating via alternate gateways if sending fails
after pre-determined time. It also allows you to check whether a message has been 
delivered. Even better you can specify a callback,
so if RedFlash is externally exposed we don't have to poll. Can then mark message 
delivery in log.   

@todo refactor. This is 'orrible
"""
    SEND_OK_RE = re.compile("ID: ([a-z,0-9,A-Z]*)$")
    SEND_OK_MULTI_RE = re.compile("ID: ([a-z,0-9,A-Z]*) To: ([0-9]*)$")
    SEND_FAIL_RE = re.compile("ERR: (.*)$")
    SEND_FAIL_MULTI_RE = re.compile("ERR: (.*) To: ([0-9]*)$")

    def __init__(self):
        gon = getattr(settings, 'GATEWAY_ORIGIN_NUMBER', None)
        self.GATEWAY_ORIGIN_NUMBER = None
        if gon:
            self.GATEWAY_ORIGIN_NUMBER = re.sub('[+ ]', '', gon)
            
    def send(self, txrecords):
        # extract numbers and index contacts by number as this will be needed
        # when processing response
        tx_by_number = {}
        message = txrecords[0].message
        notification_id = txrecords[0].notification_id
        
        for tx in txrecords:
            # here we're allowing for numbers to be input with easy-to-read
            # formatting for humans by cleansing at this point. Clickatel need
            # numbers in international format without '+' prefix. Multiple 
            # numbers to send to are comma delimited.     
            number = re.sub('[+ ]', '', tx.address.strip())
            tx_by_number[number] = tx
        
        numbers = ",".join(tx_by_number.keys())
        post_data = {'text':message,
                     'to':numbers,
                     'user':settings.GATEWAY_USER,
                     'password':settings.GATEWAY_PASSWORD,
                     'api_id':settings.GATEWAY_API_ID,
                    }
        if self.GATEWAY_ORIGIN_NUMBER:
            post_data['from'] = self.GATEWAY_ORIGIN_NUMBER
            
        if settings.GATEWAY_ENABLE_ACK:
            post_data['callback'] = 3
            
        encoded_data = urllib.urlencode(post_data)
        
        u = urllib.urlopen(settings.GATEWAY_URL,
                           data = encoded_data)

        # we've sent to gateway, so unset 'enqueued' flag
        for tx in txrecords:
            tx.enqueued = False
            tx.save()

        has_error = None
        for line in u.readlines():
            OK_MO = self.SEND_OK_RE.match(line)
            OK_MULTI_MO = self.SEND_OK_MULTI_RE.match(line)
            NOK_MO = self.SEND_FAIL_RE.match(line)
            NOK_MULTI_MO = self.SEND_FAIL_MULTI_RE.match(line)
            
            if OK_MO: ## single number posting
                id = OK_MO.groups()[0]
                tx = txrecords[0]
                tx.send_ok = True
                tx.gateway_response = id
                tx.save()
            
            elif OK_MULTI_MO: ## multiple numbers posting
                id, number = OK_MULTI_MO.groups()
                tx = tx_by_number[number]
                tx.send_ok = True
                tx.gateway_response = id
                tx.save()

            elif NOK_MO: ## error single number
                err = NOK_MO.groups()[0]
                tx = txrecords[0]
                tx.send_ok = False
                tx.gateway_response = err
                tx.save()
                has_error = err

            elif NOK_MULTI_MO: ## error multi number posting
                err, number = NOK_MULTI_MO.groups()
                tx = tx_by_number[number]
                tx.send_ok = False
                tx.gateway_response = err
                tx.save()
                has_error = err

            else:
                # @todo log the error
                pass
    
            if has_error:
                raise squawk.GatewayFailError("Error when sending: %s" % has_error, 
                                        notification_id = notification_id)
                
    def status_callback(self, callback_data):
        """ Log status information returned from the Clickatell gateway """
        gateway_id = callback_data.get('apiMsgId')
        status = callback_data.get('status')
        timestamp = callback_data.get('timestamp')
        try:
            charge = callback_data.get('charge', None)
            charge = float(charge) if charge else None
        except ValueError:
            ## @todo - log this!
            charge = None
            
        
        status_text = {'001' : 'Message unknown',
                       '002' : 'Message queued',
                       '003' : 'Delivered to gateway',
                       '004' : 'Received by recipient',  ## END OF STORY :)
                       '005' : 'Error with message',
                       '006' : 'User cancelled message delivery',
                       '007' : 'Error delivering message',
                       '008' : 'Message received by gateway',
                       '009' : 'Routing error',
                       '010' : 'Message expired',
                       '011' : 'Message queued',
                       '012' : 'Out of credit',
                       }.get(status, "STATUS UNKNOWN: %s"%status)
        
        try:
            tl = TransmissionLog.objects.get(gateway_response = gateway_id)
            tl.gateway_status = status_text
            tl.charge = charge
            if status == '004':
                tl.delivery_confirmed = True
            tl.status_timestamp = datetime.fromtimestamp(float(timestamp))
            tl.save()
        except TransmissionLog.DoesNotExist:
            ## @todo - log this!!
            pass
