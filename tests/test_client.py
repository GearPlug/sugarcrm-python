import os
from unittest import TestCase
from sugarcrm.client import Client


class SugarCRMTestCases(TestCase):
    def setUp(self):
        self.server_url = os.environ.get('server_url')
        self.username = os.environ.get('username')
        self.password = os.environ.get('password')
        self.module = os.environ.get('module')

        self.client = Client(self.server_url, self.username, self.password)

    def test_login(self):
        self.assertIsInstance(self.client.session_id, str)

    def test_get_available_modules(self):
        response = self.client.get_available_modules(self.module)
        self.assertIn('modules', response)

    def test_get_entries_count(self):
        response = self.client.get_entries_count(self.module)
        self.assertIn('result_count', response)

    def test_get_entry_list(self):
        response = self.client.get_entry_list(self.module)
        self.assertIn('entry_list', response)

    def test_get_module_fields(self):
        response = self.client.get_module_fields(self.module)
        self.assertIn('module_fields', response)
