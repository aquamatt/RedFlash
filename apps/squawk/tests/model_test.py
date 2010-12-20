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
                    enabled=True,
                    number='007')
        json = c.json()

        comparable = '{"number": "007", "name": "Test Contact", "slug": "test-contact"}'
        self.assertEquals(json, comparable)