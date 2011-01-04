# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
import simplejson as json

class SquawkException(Exception):
    def __init__(self, message = "", notification_id = None):
        Exception.__init__(self, message)
        data = {}
        data['message'] = message
        if notification_id != None:
            data['notification_id'] = notification_id
        self.message = json.dumps(data)
        self.notification_id = notification_id

    def __str__(self):
        return self.message
       
class InvalidContactError(SquawkException): pass
class InvalidGroupError(SquawkException): pass
class InvalidEventError(SquawkException): pass
class DisabledContactError(SquawkException): pass
class DisabledGroupError(SquawkException): pass
class DisabledEventError(SquawkException): pass
class PartialSendError(SquawkException): pass
class GatewayFailError(SquawkException): pass
