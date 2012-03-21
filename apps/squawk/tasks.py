# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
""" Utilities for managing the sending of messages via SMS and other channels
"""
import squawk.gateway
import squawk.models
from celery.task import task

@task
def transmit(txids, method=squawk.models.SMS):
    """ Destined to be run on a celery queue, txids is a list
of TransmissionLog IDs for the entries to be SMSed. or TWEETed 

method can take values squawk.models.[SMS|TWITTER|EMAIL]
"""
    if method == squawk.models.SMS:
        squawk.gateway.gateway().send(txids)
    elif method == squawk.models.TWITTER:
        squawk.gateway.twitter().send(txids)
    elif method == squawk.models.EMAIL:
        squawk.gateway.email().send(txids)
    else:
        raise Exception("Unknown transmit method id: %s" % method)

