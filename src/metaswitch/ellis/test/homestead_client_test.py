import unittest
from metaswitch.ellis.homestead_client import HomesteadClient
import responses


class TestHomesteadClient(unittest.TestCase):
    def setUp(self):
        self.hs = HomesteadClient("hs.example.com")

class TestHomesteadClientIRS(TestHomesteadClient):
    @responses.activate
    def test_create_irs(self):
        responses.add(responses.POST, 'http://hs.example.com:8889/irs',
                      adding_headers={'Location': '/irs/abcde/'}, status=201)
        result = self.hs.create_irs()
        self.assertEqual('/irs/abcde/', result)

    @responses.activate
    def test_create_irs_failure(self):
        responses.add(responses.POST, 'http://hs.example.com:8889/irs',
                      body='', status=500)
        result = self.hs.create_irs()
        self.assertIsNone(result)

    @responses.activate
    def test_delete_irs_200(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde',
                      status=200)
        result = self.hs.delete_irs('/irs/abcde')
        self.assertTrue(result)

    @responses.activate
    def test_delete_irs_201(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde',
                      status=201)
        result = self.hs.delete_irs('/irs/abcde')
        self.assertTrue(result)

    @responses.activate
    def test_delete_irs_failed(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde',
                      status=403)
        result = self.hs.delete_irs('/irs/abcde')
        self.assertFalse(result)


class TestHomesteadClientSP(TestHomesteadClient):
    @responses.activate
    def test_create_sp(self):
        responses.add(responses.POST, 'http://hs.example.com:8889/irs/abcde/service-profiles',
                      adding_headers={'Location': '/irs/abcde/service-profiles/1234'}, status=201)
        result = self.hs.create_sp('/irs/abcde')
        self.assertEqual('/irs/abcde/service-profiles/1234', result)

    @responses.activate
    def test_create_sp_failure(self):
        responses.add(responses.POST, 'http://hs.example.com:8889/irs/abcde/service-profiles',
                      body='', status=500)
        result = self.hs.create_sp('/irs/abcde')
        self.assertIsNone(result)

    @responses.activate
    def test_delete_sp_200(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde/service-profiles/1234',
                      status=200)
        result = self.hs.delete_sp('/irs/abcde/service-profiles/1234')
        self.assertTrue(result)

    @responses.activate
    def test_delete_sp_201(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde/service-profiles/1234',
                      status=201)
        result = self.hs.delete_sp('/irs/abcde/service-profiles/1234')
        self.assertTrue(result)

    @responses.activate
    def test_delete_sp_failed(self):
        responses.add(responses.DELETE, 'http://hs.example.com:8889/irs/abcde/service-profiles/1234',
                      status=403)
        result = self.hs.delete_sp('/irs/abcde/service-profiles/1234')
        self.assertFalse(result)


class TestHomesteadClientIMPU(TestHomesteadClient):
    pass


class TestHomesteadClientIRS(TestHomesteadClient):
    pass
