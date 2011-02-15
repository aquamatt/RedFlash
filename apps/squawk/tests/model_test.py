# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details
from django.test import TestCase
from squawk.models import Contact
import squawk.lib

class TestContact(TestCase):
    def test_serialization(self):
        c = Contact(name='Test Contact', 
                    slug='test-contact',
                    enabled=True)
        json = c.json()

        comparable = '{"name": "Test Contact", "slug": "test-contact"}'
        self.assertEquals(json, comparable)
