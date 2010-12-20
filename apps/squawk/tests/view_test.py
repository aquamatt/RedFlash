# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
from django.test import TestCase
import squawk.lib
from squawk.gateway import DummyGateway

class TestContactHandlers(TestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        squawk.lib.GATEWAY = DummyGateway()

    def test_get_contact_data(self):
        response = self.client.get('/contact/demo-user/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 200)

    def test_get_disabled_contact_data(self):
        response = self.client.get('/contact/disabled-user/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 404)

    def test_get_contact_non_admin(self):
        response = self.client.get('/contact/demo-user/', data = {'api_key' : self.valid_key})
        self.assertEqual(response.status_code, 403)
        
    def test_get_contact_invalid_user(self):
        response = self.client.get('/contact/fake-user/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 404)

    def test_get_contact_invalid_user_invalid_key(self):
        response = self.client.get('/contact/fake-user/', data = {'api_key' : self.invalid_key})
        self.assertEqual(response.status_code, 403)

    def test_get_contact_no_api_key(self):
        response = self.client.get('/contact/demo-user/') 
        self.assertEqual(response.status_code, 500)

    def test_post_contact_no_api_key(self):
        response = self.client.post('/contact/demo-user/') 
        self.assertEqual(response.status_code, 500)
        
    def test_post_to_contact(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 201)

    def test_post_to_disabled_contact(self):
        response = self.client.post('/contact/disabled-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 404)

    def test_post_to_contact_empty_message(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,
                                                                   'message':''})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, "Empty message")

    def test_post_to_contact_no_message(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.valid_key,})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, "Empty message")

    def test_post_to_contact_invalid_key(self):
        response = self.client.post('/contact/demo-user/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 403)

    def test_post_to_fake_contact(self):
        response = self.client.post('/contact/fake-user/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 404)
    
    def test_post_to_fake_contact_invalid_key(self):
        response = self.client.post('/contact/fake-user/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 403)

    def test_put_request(self):
        response = self.client.put('/contact/demo-user/', data = {'api_key':self.valid_key})
        self.assertEqual(response.status_code, 403)


class TestGroupHandlers(TestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        squawk.lib.GATEWAY = DummyGateway()

    def test_get_group_data(self):
        response = self.client.get('/group/demo-group/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 200)

    def test_get_disabled_group_data(self):
        response = self.client.get('/group/disabled-group/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 404)

    def test_get_group_non_admin(self):
        response = self.client.get('/group/demo-group/', data = {'api_key' : self.valid_key})
        self.assertEqual(response.status_code, 403)
        
    def test_get_group_invalid_user(self):
        response = self.client.get('/group/fake-group/', data = {'api_key' : self.valid_admin})
        self.assertEqual(response.status_code, 404)

    def test_get_group_invalid_user_invalid_key(self):
        response = self.client.get('/group/fake-group/', data = {'api_key' : self.invalid_key})
        self.assertEqual(response.status_code, 403)

    def test_get_group_no_api_key(self):
        response = self.client.get('/group/demo-group/') 
        self.assertEqual(response.status_code, 500)

    def test_post_group_no_api_key(self):
        response = self.client.post('/group/demo-group/') 
        self.assertEqual(response.status_code, 500)
        
    def test_post_to_group(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 201)

    def test_post_to_disabled_group(self):
        response = self.client.post('/group/disabled-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 404)

    def test_post_to_group_empty_message(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,
                                                                   'message':''})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, "Empty message")

    def test_post_to_group_no_message(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.valid_key,})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, "Empty message")

#    def test_post_to_group_with_some_invalid_users(self):
#        """ @todo: Would need to bork the DB to do this so not testing... """
#        response = self.client.post('/group/demo-partial-group/', data = {'api_key':self.valid_key,
#                                                                   'message':'The message'})
#        self.assertEqual(response.status_code, 202)


    def test_post_to_group_invalid_key(self):
        response = self.client.post('/group/demo-group/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 403)

    def test_post_to_fake_group(self):
        response = self.client.post('/group/fake-group/', data = {'api_key':self.valid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 404)
    
    def test_post_to_fake_group_invalid_key(self):
        response = self.client.post('/group/fake-group/', data = {'api_key':self.invalid_key,
                                                                   'message':'The message'})
        self.assertEqual(response.status_code, 403)

    def test_put_request(self):
        response = self.client.put('/group/demo-group/', data = {'api_key':self.valid_key})
        self.assertEqual(response.status_code, 403)

class TestEventHandlers(TestCase):
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        squawk.lib.GATEWAY = DummyGateway()

    def test_event_invalid_key(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.invalid_key})
        self.assertEqual(response.status_code, 403)
    
    def test_event_no_api_key(self):
        response = self.client.post('/event/server-overload/')
        self.assertEqual(response.status_code, 500)

    def test_event_fake_event(self):
        response = self.client.post('/event/fake-event/', data = {'api_key':self.valid_key})
        self.assertEqual(response.status_code, 404)
        
    def test_event_fake_event_invalid_key(self):
        response = self.client.post('/event/fake-event/', data = {'api_key':self.invalid_key})
        self.assertEqual(response.status_code, 403)
    
    def test_valid_event_send(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.valid_key})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(squawk.lib.GATEWAY.LAST_MESSAGE, "Test server overload event : ")
                
    def test_send_to_disabled_event(self):
        response = self.client.post('/event/disabled-event/', data = {'api_key':self.valid_key})
        self.assertEqual(response.status_code, 404)
        
    def test_event_additional_args(self):
        response = self.client.post('/event/server-overload/', data = {'api_key':self.valid_key,
                                                                       'x' : 10,
                                                                       'y' : 'hello'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(squawk.lib.GATEWAY.LAST_MESSAGE, "Test server overload event hello: 10")
        
class TestLogging(TestCase):
    """ Meaningless until refactor of gateway to extract logging. """
    fixtures = ['testdata']
    
    def setUp(self):
        self.valid_key = '12345678901234567890'
        self.valid_admin = '1af89877901234567890'
        self.invalid_key = '11111111111111111111'
        squawk.lib.GATEWAY = DummyGateway()

    