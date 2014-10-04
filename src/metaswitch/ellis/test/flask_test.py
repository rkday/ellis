import os
import metaswitch.ellis.main as ellis
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, ellis.app.config['DATABASE'] = tempfile.mkstemp()
        ellis.app.config['TESTING'] = True
        self.app = ellis.app.test_client()
        #ellis.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(ellis.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/accounts/')
        self.assertEquals(405, rv.status_code)
