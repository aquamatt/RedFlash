# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" SMS gateway implementation for Nexmo
"""
import logging
import re
import squawk
import urllib
import simplejson
from datetime import datetime
from django.conf import settings
from squawk.models import TransmissionLog

class NexmoGateway(object):
    """ Gateway class for Nexmo

Settings variables:

*    GATEWAY_ORIGIN_NUMBER can be alphanumeric in this case; it's the 'From field' and defaults to Redflash if not set.
* GATEWAY_URL - ideally the HTTPS version, https://rest.nexmo.com/sms/json

* GATEWAY_[USER|PASSWORD] are your key and secret. GATEWAY_API_ID is not used
* GATEWAY_ENABLE_ACK should be set True if you have set callbacks in your Nexmo account and this instance is running on that callback URL
* GATEWAY_CALLBACK_METHOD should be set to 'POST' or 'GET' according to how you set this in your account settings

"""
    def __init__(self):
        self.GATEWAY_ORIGIN_NUMBER = \
            getattr(settings, 'GATEWAY_ORIGIN_NUMBER', "Redflash")
            
    def send(self, txrecords):
        # extract numbers and index contacts by number as this will be needed
        # when processing response
        # txrecords is a list of TransmissionLog IDs
        txrecords = TransmissionLog.objects.filter(pk__in=txrecords)
        tx_by_number = {}
        message = txrecords[0].message
        notification_id = txrecords[0].notification_id
        
        post_data = {'text':message,
                     'type': 'text',
                     'from' : self.GATEWAY_ORIGIN_NUMBER,
                     'username':settings.GATEWAY_USER,
                     'password':settings.GATEWAY_PASSWORD,
                     'status-report-req' : settings.GATEWAY_ENABLE_ACK,
                    }


# loop over adding 'to' field being the number and client-ref the tx
# record ID so this can be correlated in the response
        has_error = None
        for tx in txrecords:
            post_data['to'] = re.sub('[+ ]', '', tx.address.strip())
            post_data['client-ref'] = tx.id
            encoded_data = urllib.urlencode(post_data)
            try:
                u = urllib.urlopen(settings.GATEWAY_URL,
                           data = encoded_data)
            except Exception, ex:
                has_error = str(ex)
                break

            tx.enqueued = False
            tx.save()

            response = simplejson.loads("".join(u.readlines()))

            try:
                tx.charge = sum(
                            [float(r.get('message-price', 0.0))
                                for r in response['messages']
                            ]
                        )
                status = int(response['messages'][0]['status'])
                status_type = {
                        0 : 'Delivered',
                        1 : 'Unknown',
                        2 : 'Absent Subscriber - Temporary',
                        3 : 'Absent Subscriber - Permenant',
                        4 : 'Call barred by user',
                        5 : 'Portability Error',
                        6 : 'Anti-Spam Rejection',
                        7 : 'Handset Busy',
                        8 : 'Network Error',
                        9 : 'Illegal Number',
                        10 : 'Invalid Message',
                        11 : 'Unroutable',
                        99 : 'General Error',
                             } [status]
                           
                tx.status_timestamp = datetime.now()
                if status == 0:
                    tx.gateway_response = status_type
                    tx.send_ok = True
                else:
                    # error occured
                    tx.send_ok = False
                    tx.gateway_response = \
                        "%s: %s" % (status_type, 
                                response['messages'][0]['error-text'])
                    has_error = tx.gateway_response
            except Exception, ex:
                has_error = "ERROR: %s" % str(ex)
                tx.gateway_response = has_error

            tx.save()
             
        if has_error:
                raise squawk.GatewayFailError("Error when sending: %s" % has_error, notification_id = notification_id)
                
    def status_callback(self, callback_data):
        """ Log status information returned from the gateway """
        txid = int(callback_data.get('client-ref'))
        try:
            tl = TransmissionLog.objects.get(pk = txid)

            tl.status_timestamp = \
                    datetime.strptime(
                            callback_data.get('message-timestamp'),
                            "%Y-%m-%d %H:%M:%S")
            status = callback_data.get('status')

            response_code = int(callback_data.get('err-code'))
            response_message = {
                        0:  'Delivered',
                        1:  'Unknown',
                        2:  'Absent Subscriber - Temporary',
                        3:  'Absent Subscriber - Permenant',
                        4:  'Call barred by user',
                        5:  'Portability Error',
                        6:  'Anti-Spam Rejection',
                        7:  'Handset Busy',
                        8:  'Network Error',
                        9:  'Illegal Number',
                        10: 'Invalid Message',
                        11: 'Unroutable',
                        99: 'General Error',
                   }[response_code]
            tl.gateway_status = response_message
            if response_code == 0:
                tl.delivery_confirmed = True

            tl.save()
        except TransmissionLog.DoesNotExist:
## @todo log this!
            pass
        except Exception, ex:
            pass

    def inbound_callback(self, callback_data):
        logger = logging.getLogger("redflash")
        logger.info("Received inbound:")
        for k,v in callback_data.items():
            logger.info(" -- %s = %s " % (k,v))
