# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from squawk.gateway.dummy import DummyGateway
from squawk.models import TransmissionLog
import squawk.lib
import simplejson as json

class SquawkTestCase(TestCase):
    def assertIsJSON(self, s):
        try:
            rval = json.loads(s)
        except json.JSONDecodeError:
            self.fail("Value '%s' is not a valid JSON string" %s)

    def assertStatus(self, response, status):
        if response.status_code != status:
            self.fail("Status %d != %d" % (response.status_code, status))

    def makeJSONmessage(self, msg):
        return '{"message": "%s"}' % msg

class TestContactHandlers(SquawkTestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        # force gateway to re-load and be the dummy
        squawk.gateway.gateway(new_gateway = "DummyGateway") 
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True

    def test_get_contact_data(self):
        response = self.client.get('/contact/demo-user/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 200)
        self.assertIsJSON(response.content)

    def test_get_disabled_contact_data(self):
        response = self.client.get('/contact/disabled-user/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_get_contact_non_admin(self):
        response = self.client.get('/contact/demo-user/', data = {'api_key' : self.valid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)
        
    def test_get_contact_invalid_user(self):
        response = self.client.get('/contact/fake-user/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_get_contact_invalid_user_invalid_key(self):
        response = self.client.get('/contact/fake-user/', data = {'api_key' : self.invalid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_get_contact_no_api_key(self):
        response = self.client.get('/contact/demo-user/') 
        self.assertStatus(response, 500)
        self.assertIsJSON(response.content)

    def test_post_contact_no_api_key(self):
        response = self.client.post('/contact/demo-user/') 
        self.assertStatus(response, 500)
        self.assertIsJSON(response.content)
        
    def test_post_to_contact(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 201)
        self.assertIsJSON(response.content)
        rval = json.loads(response.content)
        self.assertEqual(rval['message'], 'OK')
        self.assertTrue('notification_id' in rval)
        # don't know the notification ID but know it will be 32 chars long
        self.assertEqual(len(rval['notification_id']), 32)

    def test_post_to_disabled_contact(self):
        response = self.client.post('/contact/disabled-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_post_to_contact_empty_message(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':''})
        self.assertStatus(response, 500)
        self.assertEqual(response.content, self.makeJSONmessage("Empty message"))
        self.assertIsJSON(response.content)

    def test_post_to_contact_no_message(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,})
        self.assertStatus(response, 500)
        self.assertEqual(response.content,  self.makeJSONmessage("Empty message"))
        self.assertIsJSON(response.content)

    def test_post_to_contact_invalid_key(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_post_to_fake_contact(self):
        response = self.client.post('/contact/fake-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

#    def test_post_to_enabled_contact_no_enabled_endpoints(self):
#        self.fail("No test")
    
    def test_post_to_fake_contact_invalid_key(self):
        response = self.client.post('/contact/fake-user/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_put_request(self):
        response = self.client.put('/contact/demo-user/', data = {'api_key':self.valid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

class TestGroupHandlers(SquawkTestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        # force gateway to re-load
        squawk.gateway.gateway(new_gateway = "DummyGateway")
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True

    def test_get_group_data(self):
        response = self.client.get('/group/demo-group/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 200)
        self.assertIsJSON(response.content)

    def test_get_disabled_group_data(self):
        response = self.client.get('/group/disabled-group/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_get_group_non_admin(self):
        response = self.client.get('/group/demo-group/', data = {'api_key' : self.valid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)
        
    def test_get_group_invalid_user(self):
        response = self.client.get('/group/fake-group/', data = {'api_key' : self.valid_admin})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_get_group_invalid_user_invalid_key(self):
        response = self.client.get('/group/fake-group/', data = {'api_key' : self.invalid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_get_group_no_api_key(self):
        response = self.client.get('/group/demo-group/') 
        self.assertStatus(response, 500)
        self.assertIsJSON(response.content)

    def test_post_group_no_api_key(self):
        response = self.client.post('/group/demo-group/') 
        self.assertStatus(response, 500)
        self.assertIsJSON(response.content)
        
    def test_post_to_group(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 201)
        self.assertIsJSON(response.content)
        rval = json.loads(response.content)
        self.assertEqual(rval['message'], 'OK')
        self.assertTrue('notification_id' in rval)
        # don't know the notification ID but know it will be 32 chars long
        self.assertEqual(len(rval['notification_id']), 32)

    def test_post_to_disabled_group(self):
        response = self.client.post('/group/disabled-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)

    def test_post_to_group_empty_message(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,
                                                                   'message':''})
        self.assertStatus(response, 500)
        self.assertEqual(response.content, self.makeJSONmessage("Empty message"))
        self.assertIsJSON(response.content)

    def test_post_to_group_no_message(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,})
        self.assertStatus(response, 500)
        self.assertEqual(response.content, self.makeJSONmessage("Empty message"))
        self.assertIsJSON(response.content)

#    def test_post_to_group_with_some_invalid_users(self):
#        """ @todo: Would need to bork the DB to do this so not testing... actually...
# on second thoughts... this occurs if the phone number is bad and the gateway returns
# error. Need to sort this test."""
#        response = self.client.post('/group/demo-partial-group/', data = {'api_key':self.valid_key,
#                                                                   'message':'The message'})
#        self.assertStatus(response, 202)


    def test_post_to_group_invalid_key(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_post_to_fake_group(self):
        response = self.client.post('/group/fake-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)
    
    def test_post_to_fake_group_invalid_key(self):
        response = self.client.post('/group/fake-group/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

    def test_put_request(self):
        response = self.client.put('/group/demo-group/', data = {'api_key':self.valid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)

class TestEventHandlers(SquawkTestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        # force gateway to re-load
        squawk.gateway.gateway(new_gateway = "DummyGateway")
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True

    def test_event_invalid_key(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.invalid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)
    
    def test_event_no_api_key(self):
        response = self.client.post('/event/server-overload/')
        self.assertStatus(response, 500)
        self.assertIsJSON(response.content)

    def test_event_fake_event(self):
        response = self.client.post('/event/fake-event/', data = {'api_key':self.valid_key})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)
        
    def test_event_fake_event_invalid_key(self):
        response = self.client.post('/event/fake-event/', data = {'api_key':self.invalid_key})
        self.assertStatus(response, 403)
        self.assertIsJSON(response.content)
    
    def test_valid_event_send(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.valid_key})
        self.assertStatus(response, 201)
        #squawk.lib.dequeue()
        self.assertEqual(squawk.gateway.gateway().LAST_MESSAGE, "Test server overload event : ")
        self.assertIsJSON(response.content)
                
    def test_send_to_disabled_event(self):
        response = self.client.post('/event/disabled-event/', data = {'api_key':self.valid_key})
        self.assertStatus(response, 404)
        self.assertIsJSON(response.content)
        
    def test_event_additional_args(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.valid_key,
                                                                       'x' : 10,
                                                                       'y' : 'hello'})
        self.assertStatus(response, 201)
        #squawk.lib.dequeue()
        self.assertEqual(squawk.gateway.gateway().LAST_MESSAGE, "Test server overload event hello: 10")
        self.assertIsJSON(response.content)

class TestDeliveryStatusCallback(SquawkTestCase):
    """ Test callback handlers for delivery status. """
    fixtures = ['testdata']

    def setUp(self):
        self.valid_key = '12345678901234567890'
        # force gateway to re-load
        squawk.gateway.gateway(new_gateway = "DummyGateway")
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True
        squawk.gateway.gateway().GATEWAY_MID = squawk.lib.create_notification_id()
        settings.GATEWAY_ENABLE_ACK = True
        settings.GATEWAY_CALLBACK_METHOD = "POST"

        # create the sample sent message which will have the gateway response code set
        # as above
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        #squawk.lib.dequeue()                                                                   
        self.response_timestamp = datetime(2008, 1, 10, 21, 20)
        
    def test_callback_delivered(self):
        """ This tests the demo callback handler NOT one of the real handlers. """
        data = { 'apiMsgId' : squawk.gateway.gateway().GATEWAY_MID,
                 'status' : '004',
                 'charge' : '0.3',
                 'timestamp' : '1200000000'
                }
        response = self.client.post('/ack/', data = data)
        log_entry = TransmissionLog.objects.get(gateway_response = squawk.gateway.gateway().GATEWAY_MID)

        self.assertEqual(log_entry.charge, 0.3)
        self.assertEqual(log_entry.gateway_status, 'Received by recipient')
        self.assertTrue(log_entry.delivery_confirmed)
        self.assertEqual(log_entry.status_timestamp, self.response_timestamp)

        
    def test_callback_delivered_to_gateway(self):
        """ This tests the demo callback handler NOT one of the real handlers. """
        data = { 'apiMsgId' : squawk.gateway.gateway().GATEWAY_MID,
                 'status' : '003',
                 'charge' : '0.3',
                 'timestamp' : '1200000000'
                }
        response = self.client.post('/ack/', data = data)

        log_entry = TransmissionLog.objects.get(gateway_response = squawk.gateway.gateway().GATEWAY_MID)
        self.assertStatus(response, 200)
        self.assertEqual(log_entry.charge, 0.3)
        self.assertEqual(log_entry.gateway_status, 'Delivered to gateway')
        self.assertFalse(log_entry.delivery_confirmed)
        self.assertEqual(log_entry.status_timestamp, self.response_timestamp)

        
class TestClickatellDeliveryStatusCallback(SquawkTestCase):
    """ Test callback handlers for delivery status in the Clickatell
handler. """
    fixtures = ['testdata']

    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.GATEWAY_MID = squawk.lib.create_notification_id()
        self.init_gateway("DummyGateway")
        settings.GATEWAY_ENABLE_ACK = True
        settings.GATEWAY_CALLBACK_METHOD = "POST"

        # create the sample sent message which will have the gateway response code set
        # as above
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        #squawk.lib.dequeue()                                                                   
        self.response_timestamp = datetime(2008, 1, 10, 21, 20)

    def init_gateway(self, gateway):
        # force gateway to re-load
        squawk.gateway.gateway(new_gateway = gateway)
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True
        squawk.gateway.gateway().GATEWAY_MID = self.GATEWAY_MID
        settings.GATEWAY_ENABLE_ACK = True
        
    def test_callback_delivered(self):
        # switch to clickatell to test that handler
        self.init_gateway("ClickatellGateway")
        data = { 'apiMsgId' : squawk.gateway.gateway().GATEWAY_MID,
                 'status' : '004',
                 'charge' : '0.3',
                 'timestamp' : '1200000000'
                }
        response = self.client.post('/ack/', data = data)
        log_entry = TransmissionLog.objects.get(gateway_response = squawk.gateway.gateway().GATEWAY_MID)

        self.assertStatus(response, 200)
        self.assertEqual(log_entry.charge, 0.3)
        self.assertEqual(log_entry.gateway_status, 'Received by recipient')
        self.assertTrue(log_entry.delivery_confirmed)
        self.assertEqual(log_entry.status_timestamp, self.response_timestamp)

        
    def test_callback_delivered_to_gateway(self):
        self.init_gateway("ClickatellGateway")
        data = { 'apiMsgId' : squawk.gateway.gateway().GATEWAY_MID,
                 'status' : '003',
                 'charge' : '0.3',
                 'timestamp' : '1200000000'
                }
        response = self.client.post('/ack/', data = data)

        log_entry = TransmissionLog.objects.get(gateway_response = squawk.gateway.gateway().GATEWAY_MID)
        self.assertStatus(response, 200)
        self.assertEqual(log_entry.charge, 0.3)
        self.assertEqual(log_entry.gateway_status, 'Delivered to gateway')
        self.assertFalse(log_entry.delivery_confirmed)
        self.assertEqual(log_entry.status_timestamp, self.response_timestamp)

        
class TestLogging(SquawkTestCase):
    """ Basic test that log entries can be made via dummy gateway. """
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        # force gateway to re-load
        squawk.gateway.gateway(new_gateway = "DummyGateway")
        # we'll explicitly dequeue in the tests
        settings.SEND_IN_PROCESS = True
        squawk.gateway.gateway().GATEWAY_MID = squawk.lib.create_notification_id()

    def test_contact_log_entry(self):   
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The second message'})
        #squawk.lib.dequeue()
        try:
            log_entry = TransmissionLog.objects.get(gateway_response = squawk.gateway.gateway().GATEWAY_MID)
            self.assertEqual(log_entry.gateway_response, squawk.gateway.gateway().GATEWAY_MID) 
            self.assertEqual(log_entry.message, 'The second message')
            self.assertTrue(log_entry.send_ok)
            self.assertEqual(log_entry.notification_type, 'contact')
            self.assertEqual(log_entry.notification_slug, 'demo-user')
        except TransmissionLog.MultipleObjectsReturned:
            self.fail("More than one log entry found on send to contact")
        
    def test_group_log_entry(self):   
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The second message'}
                                    )
        #squawk.lib.dequeue()
        rval = json.loads(response.content)
        nid = rval['notification_id']
        log_entries = TransmissionLog.objects.filter(notification_id = nid)
        self.assertEqual(len(log_entries), 2)

        # check log entry for send to each contact in the group is right
        contacts = []
        for log_entry in log_entries:
            self.assertEqual(log_entry.gateway_response, squawk.gateway.gateway().GATEWAY_MID) 
            self.assertEqual(log_entry.message, 'The second message')
            self.assertTrue(log_entry.send_ok)
            self.assertEqual(log_entry.notification_type, 'group')
            self.assertEqual(log_entry.notification_slug, 'demo-group')
            self.assertFalse(log_entry.contact in contacts)
            contacts.append(log_entry.contact)
    
