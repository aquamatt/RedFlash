# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Twitter gateway implementation
"""
import twitter.api
import squawk
from django.conf import settings
from squawk.models import TransmissionLog
from twitter.oauth import OAuth

class TwitterGateway(object):
    """ xx1xx) Refactor gateways into separate files

2) Using Python Twitter Tools

import twitter.api
twitter = twitter.api.Twitter(auth=OAuth("xxx","yyy","uS6hO2sV6tDKIOeVjhnFnQ","MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk"))
twitter.direct_messages.new(user="aquamatt", text="foobar")

First two OAuth keys are generated easily with command line tool. Last two are application ones - think we can stick with those that come with twitter tools though.

To generate first keys:

* Get python twitter tools (installed by requriements)
* run "twitter authorize"
* Copy values from ~/.twitter_oauth into settings.py or, better, /etc/redflash.py

"""
    def __init__(self):
        self.twitter = twitter.api.Twitter(auth=OAuth(settings.TWITTER_TOKEN, 
                                   settings.TWITTER_KEY,
                                   settings.TWITTER_CONN_SECRET,
                                   settings.TWITTER_CONN_SECRET_KEY))

    def send(self, txrecords):
        """ Send each individually """
        # txrecords is a list of TransmissionLog IDs
        txrecords = TransmissionLog.objects.filter(pk__in=txrecords)
        errors = []
        for tx in txrecords:
            twitterid = tx.address.lstrip('@')
            try:
                rv = self.twitter.direct_messages.new(user=twitterid, text=tx.message)
                tx.gateway_response = "%d" % rv['id']
                tx.enqueued = False
                tx.send_ok = True
                tx.gateway_status = "Sent to gateway"
                tx.save()
            except Exception, ex:
                tx.enqueued = False
                tx.send_ok = False
                tx.gateway_status = str(ex)[:400]
                tx.save()
                errors.append(tx)

        if errors:
            notification_id = errors[0].notification_id
            raise squawk.GatewayFailError("Error when sending tweets for notification %s (%s)" % notification_id,
                                    notification_id = notification_id)
            
