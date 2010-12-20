# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

class InvalidContactError(Exception): pass
class InvalidGroupError(Exception): pass
class InvalidEventError(Exception): pass
class DisabledContactError(Exception): pass
class DisabledGroupError(Exception): pass
class DisabledEventError(Exception): pass
class PartialSendError(Exception): pass