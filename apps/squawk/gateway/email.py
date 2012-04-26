# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Email gateway implementation
"""
import squawk
from django.core.mail import EmailMessage
from squawk.models import TransmissionLog

class EmailGateway(object):
    """ Email via standard django email system. With django-celery-email this is 
automagically asynchronous.
"""
    def __init__(self):
        super(EmailGateway, self).__init__()

    def send(self, txrecords):
        """ Send one email with a long bcc list. """
        # txrecords is a list of TransmissionLog IDs
        txrecords = TransmissionLog.objects.filter(pk__in=txrecords)
        email_addresses = [tx.address for tx in txrecords]

        try:
            message = EmailMessage(
                    subject = "RedFlash alert",
                    body = """
This message is automatically generated. 

A RedFlash alert has been triggered with the following message: %s

DO NOT REPLY TO THIS EMAIL. ANY MAIL SENT TO THIS ADDRESS WILL BE IGNORED.
Notification ID: %s                    
                    """ % (tx.message, tx.notification_id),
                    bcc = email_addresses,
                    )
            message.send(fail_silently = False)
            # send mail
            for tx in txrecords:
                tx.gateway_response = "sent"
                tx.enqueued = False
                tx.send_ok = True
                tx.gateway_status = "Email sent"
                tx.save()
        except Exception, ex:
            for tx in txrecords:
                tx.gateway_response = "ERROR" 
                tx.enqueued = False
                tx.send_ok = False
                tx.gateway_status = str(ex)[:400]
                tx.save()
            notification_id = txrecords[0].notification_id
            raise squawk.GatewayFailError("Error when sending email for notification %s (%s)" % (notification_id, txrecords[0].gateway_status),
                                    notification_id = notification_id)
            


