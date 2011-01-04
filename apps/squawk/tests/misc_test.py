# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
from django.test import TestCase
from squawk import SquawkException
import simplejson as json

class TestExceptions(TestCase):
    def test_squawk_exception_no_id(self):
        se = SquawkException("Hello world")
        try:
            rval = json.loads(se.message)
        except json.JSONDecodeError:
            self.fail('SquawkException message is not a JSON string')

        self.assertTrue('message' in rval)
        self.assertFalse('notification_id' in rval)
        self.assertEqual(rval['message'], 'Hello world')
        self.assertEqual(se.notification_id, None)
        
    def test_squawk_exception_with_id(self):
        se = SquawkException("Hello world", '123A')
        try:
            rval = json.loads(se.message)
        except json.JSONDecodeError:
            self.fail('SquawkException message is not a JSON string')

        self.assertTrue('message' in rval)
        self.assertTrue('notification_id' in rval)
        self.assertEqual(rval['notification_id'], '123A')
        self.assertEqual(rval['message'], 'Hello world')
        self.assertEqual(se.notification_id, '123A')

    def test_squawk_exception_str_same_as_message(self):
        se = SquawkException(message = "Hello world", notification_id = 1000)
        self.assertEqual(str(se), se.message)
         
