# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Twitter gateway implementation
"""
import twitter.api
from django.conf import settings
from squawk.models import TransmissionLog
from twitter.oauth import OAuth

class TwitterGateway(object):
    """ xx1xx) Refactor gateways into separate files

2) Using Python Twitter Tools

import twitter.api
twitter = twitter.api.Twitter(auth=OAuth("15401671-rjM8kX5GjO9qI6bAOBDi5xO2ehlB3B4CdMwqH28j8","twlMosBlg2nZgYdl2hIWEa9Mdt9Wy030u8ooH3C3g","uS6hO2sV6tDKIOeVjhnFnQ","MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk"))
twitter.direct_messages.new(user="aquamatt", test="foobar")

First two OAuth keys are generated easily with command line tool. Last two are application ones - think we can stick with those that come with twitter tools though.

To generate first keys:

* Get python twitter tools (installed by requriements)
* run "twitter authorize"
* Copy values from ~/.twitter_oauth into settings.py or, better, /etc/redflash.py

"""
    def __init__(self):
        self.twitter = twitter.api(oauth=OAuth(settings.TWITTER_TOKEN, 
                                   settings.TWITTER_KEY,
                                   settings.TWITTER_CONN_SECRET,
                                   settings.TWITTER_CONN_SECRET_KEY))

    def send(self, txrecords):
        """ Send each individually """
        for tx in txrecords:
            twitterid = tx.address.lstrip('@')
            self.twitter.direct_messages.new(user="aquamatt", text=tx.message)

            
