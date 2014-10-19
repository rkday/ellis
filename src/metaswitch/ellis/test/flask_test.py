import os
import metaswitch.ellis.main as ellis
from metaswitch.ellis.memdb import InMemoryDatabase
from metaswitch.ellis.homestead_client import HomesteadClient
import unittest
import json
from mock import MagicMock

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        ellis.app.config['DATABASE'] = InMemoryDatabase()
        ellis.app.config['TESTING'] = True
        ellis.app.secret_key = "abcde"
        self.app = ellis.app.test_client()

    def tearDown(self):
        ellis.app.config['DATABASE'] = None

class UserCreationTestCase(FlaskTestCase):
    user = {"username": "test",
            "password": "test1234",
            "full_name": "Test McTestington",
            "email": "test@example.com"}

    def test_user_creation(self):
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(201, rv.status_code)

    def test_conflict(self):
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(201, rv.status_code)
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(409, rv.status_code)

    def test_bad_password(self):
        auth = {"username": "test@example.com",
                "password": "WRONG"}
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(201, rv.status_code)
        rv = self.app.post('/session/', data=json.dumps(auth))
        self.assertEquals(403, rv.status_code)

    def test_bad_user(self):
        auth = {"username": "WRONG@example.com",
                "password": "test1234"}
        rv = self.app.post('/session/', data=json.dumps(auth))
        self.assertEquals(403, rv.status_code)

    def test_login(self):
        auth = {"username": "test@example.com",
                "password": "test1234"}
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(201, rv.status_code)
        rv = self.app.post('/session/', data=json.dumps(auth))
        self.assertEquals(200, rv.status_code)

    def test_login_formdata(self):
        auth = {"username": "test@example.com",
                "password": "test1234"}
        rv = self.app.post('/accounts/', data=self.user)
        self.assertEquals(201, rv.status_code)
        rv = self.app.post('/session/', data=auth)
        self.assertEquals(200, rv.status_code)

class LineCreationTestCase(FlaskTestCase):
    user = {"username": "test@example.com",
            "password": "test1234",
            "full_name": "Test McTestington",
            "email": "test@example.com"}

    def setUp(self):
        FlaskTestCase.setUp(self)
        rv = self.app.post('/accounts/', data=json.dumps(self.user))
        self.assertEquals(201, rv.status_code)
        rv = self.app.post('/session/', data=json.dumps(self.user))
        self.assertEquals(200, rv.status_code)
        self.auth_cookies = rv.headers['Set-Cookie']

    def test_get_lines(self):
        rv = self.app.get('/accounts/test@example.com/numbers/', headers={"Cookie": self.auth_cookies})
        self.assertEquals(200, rv.status_code)
        self.assertEqual('{"numbers": []}', rv.get_data(as_text=True))

    def test_new_line(self):
        mock_hs = MagicMock(HomesteadClient)
        ellis.app.config['HOMESTEAD_CLIENT'] = mock_hs
        rv = self.app.post('/accounts/test@example.com/numbers/', headers={"Cookie": self.auth_cookies})
        self.assertEquals(200, rv.status_code)
        rv = self.app.get('/accounts/test@example.com/numbers/', headers={"Cookie": self.auth_cookies})
        self.assertEquals(200, rv.status_code)
        self.assertEqual(json.loads(rv.get_data(as_text=True))['numbers'][0]['formatted_number'], "1234")