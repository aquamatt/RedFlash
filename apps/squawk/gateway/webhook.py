# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" WebHook gateway implementation
"""
import squawk
import urllib
from squawk.models import TransmissionLog

class WebhookGateway(object):
    """ 
This allows for the chaining of alerts through to other systems. A webhook
is given a base URL (e.g. http://hooks.mysystem.com/redflash/ and messages
are sent by POSTing to the URL composed of the base URL and the message ID, e.g.: http://hooks.mysystem.com/redflash/23847aef8eeaf/ with POST arguments 'notification_id' and 'message'

Expects a 201 (or 200) response, or 500 if there was an error.
"""
    def __init__(self):
        super(WebhookGateway, self).__init__()

    def send(self, txrecords):
        """ Make webhook call. """
        # txrecords is a list of TransmissionLog IDs
        txrecords = TransmissionLog.objects.filter(pk__in=txrecords)
        errors = []

        # notify
        for tx in txrecords:
            url = tx.address.rstrip('/')
            url = "/".join([url, tx.notification_id])
            data = dict(notification_id = tx.notification_id,
                     message = tx.message)
            try:
                response = urllib.urlopen(url, 
                        data = urllib.urlencode(data))
                code = response.getcode()

                tx.gateway_response = "sent"
                tx.enqueued = False

                if code in [200, 201]:
                    tx.send_ok = True
                    tx.gateway_status = "Webhook notified"
                    tx.delivery_confirmed = True
                else:
                    tx.send_ok = False
                    tx.gateway_response = "ERROR"
                    tx.gateway_status = "Webhook call failed status %d"%code
                    errors.append(tx) 

                tx.save()

            except Exception, ex:
                tx.gateway_response = "ERROR" 
                tx.enqueued = False
                tx.send_ok = False
                tx.gateway_status = str(ex)[:400]
                tx.save()
                errors.append(tx) 

        if errors:
            notification_id = errors[0].notification_id
            raise squawk.GatewayFailError("Error when calling one or more webhooks for notification %s" % notification_id,
                                notification_id = notification_id)
        

