# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
import squawk
from datetime import datetime
from squawk.models import TransmissionLog

class DummyGateway(object):
    """ Dummy gateway for testing. """
    def __init__(self):
        self.LAST_MESSAGE = ""
        self.LAST_NOTIFICATION_ID = ""
        self.GATEWAY_MID = '1234A'
        
    def send(self, txrecords):
        """ Dummy gateway will raise Exception if message is "FAIL MESSAGE" or
return quietly otherwise. 
"""
        message = txrecords[0].message
        notification_id = txrecords[0].notification_id
        self.LAST_MESSAGE = message
        self.LAST_NOTIFICATION_ID = notification_id
        
        # allows for testing of failed gateway send
        send_ok = False if message == 'FAIL MESSAGE' else True
        
        for tx in txrecords:
            tx.enqueued = False 
            tx.send_ok = send_ok
            tx.gateway_response = self.GATEWAY_MID
            tx.save()
 
        if not send_ok:            
            raise squawk.GatewayFailError("Send failed", notification_id = notification_id)

    def status_callback(self, callback_data):
        """ demo callback handler that is based on Clickatell. 
"""
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
            al = TransmissionLog.objects.get(gateway_response = gateway_id)
            al.gateway_status = status_text
            al.charge = charge
            if status == '004':
                al.delivery_confirmed = True
            al.status_timestamp = datetime.fromtimestamp(float(timestamp))
            al.save()
        except TransmissionLog.DoesNotExist:
            ## @todo - log this!!
            pass
