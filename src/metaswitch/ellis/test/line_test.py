__author__ = 'rkd'

from metaswitch.ellis.lines import PrimaryLine
import unittest
from mock import MagicMock
from metaswitch.ellis.homestead_client import HomesteadClient
import json

class PrimaryLineTest(unittest.TestCase):
    def test_impi_creation(self):
        l = PrimaryLine(None, "sip:test@example.com")
        self.assertEqual(l.impi, "test@example.com")

    def create_fake_homestead(self):
        fake_homestead = HomesteadClient("example.com", 8889)
        fake_homestead.create_irs = MagicMock(return_value="/irs/abcde")
        fake_homestead.create_sp = MagicMock(return_value="/irs/abcde/service-profiles/12345")
        fake_homestead.create_impi = MagicMock(return_value=True)
        fake_homestead.create_impu = MagicMock(return_value=True)
        return fake_homestead

    def test_create_elsewhere(self):
        hs = self.create_fake_homestead()
        l = PrimaryLine(None, "sip:test@example.com")
        l.create_elsewhere(hs)
        self.assertFalse(l.deletion_begun)
        self.assertEqual(l.irs_uri, "/irs/abcde")
        self.assertEqual(l.sp_uri, "/irs/abcde/service-profiles/12345")
        self.assertEqual(l.impi, "test@example.com")
        self.assertEqual(l.impu, "sip:test@example.com")

    def test_create_elsewhere_irs_failed(self):
        hs = self.create_fake_homestead()
        hs.create_irs = MagicMock(return_value=None)

        l = PrimaryLine(None, "sip:test@example.com")
        l.create_elsewhere(hs)
        self.assertTrue(l.deletion_begun)
        self.assertIsNone(l.irs_uri)
        self.assertIsNone(l.sp_uri)
        self.assertEqual(l.impi, "test@example.com")
        self.assertEqual(l.impu, "sip:test@example.com")

    def test_create_elsewhere_impi_failed(self):
        hs = self.create_fake_homestead()
        hs.create_impi = MagicMock(return_value=False)

        l = PrimaryLine(None, "sip:test@example.com")
        l.create_elsewhere(hs)
        self.assertTrue(l.deletion_begun)
        self.assertEqual(l.irs_uri, "/irs/abcde")
        self.assertIsNone(l.sp_uri)
        self.assertEqual(l.impi, "test@example.com")
        self.assertEqual(l.impu, "sip:test@example.com")

    def test_create_elsewhere_sp_failed(self):
        hs = self.create_fake_homestead()
        hs.create_sp = MagicMock(return_value=None)

        l = PrimaryLine(None, "sip:test@example.com")
        l.create_elsewhere(hs)
        self.assertTrue(l.deletion_begun)
        self.assertEqual(l.irs_uri, "/irs/abcde")
        self.assertIsNone(l.sp_uri)
        self.assertEqual(l.impi, "test@example.com")
        self.assertEqual(l.impu, "sip:test@example.com")

    def test_create_elsewhere_impu_failed(self):
        hs = self.create_fake_homestead()
        hs.create_impu = MagicMock(return_value=False)

        l = PrimaryLine(None, "sip:test@example.com")
        l.create_elsewhere(hs)
        self.assertTrue(l.deletion_begun)
        self.assertEqual(l.irs_uri, "/irs/abcde")
        self.assertEqual(l.sp_uri, "/irs/abcde/service-profiles/12345")
        self.assertEqual(l.impi, "test@example.com")
        self.assertEqual(l.impu, "sip:test@example.com")

    def test_json(self):
        l = PrimaryLine(None, "sip:test@example.com")
        json_body = l.to_json()
        expected_json = json.loads('''{
  "formatted_number": "test",
  "gab_listed":       false,
  "number":           "test",
  "pstn":             false,
  "private_id":       "test@example.com",
  "sip_uri":          "sip:test@example.com",
  "sip_username":     "test"
}''')
        self.assertEqual(json_body, expected_json)
