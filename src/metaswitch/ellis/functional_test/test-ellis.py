import requests
import json
import unittest
import re
import sys

api_key = "eAq7qEC8ReNEWY1XNn7XktjmTptZgWPZpSzrVElKiD4"
username = "system.test3493@rkd.cw-ngv.com"
#where = "http://localhost:5000"
where = "http://ellis.staging.cw-ngv.com"

def delete_account(username):
    r = requests.get("{}/accounts/{}/numbers".format(where, username), headers={"NGV-API-Key": api_key}).json()
    if 'numbers' in r:
        for num in r['numbers']:
            requests.delete("{}/accounts/{}/numbers/{}".format(where, username, num['sip_uri']), headers={"NGV-API-Key": api_key})
    return requests.delete("{}/accounts/{}".format(where, username), headers={"NGV-API-Key": api_key})

def post_json(url, payload, **kwargs):
    return requests.post("{}{}".format(where, url), data=json.dumps(payload), allow_redirects=False, **kwargs)

def put(url, payload, **kwargs):
    return requests.put("{}{}".format(where, url), data=payload, allow_redirects=False, **kwargs)

def post_url_encoded(url, payload, **kwargs):
    return requests.post("{}{}".format(where, url), data=payload, allow_redirects=False, **kwargs)

def delete(url, **kwargs):
    return requests.delete("{}{}".format(where, url), allow_redirects=False, **kwargs)

def get(url, **kwargs):
    return requests.get("{}{}".format(where, url), allow_redirects=False, **kwargs)

def post_query_params(url, payload, **kwargs):
    query_params = "&".join(["{}={}".format(k, v) for (k, v) in payload.items()])
    return requests.post("{}{}?{}".format(where, url, query_params), allow_redirects=False, **kwargs)

    
class NewAccountTest(unittest.TestCase):
    def tearDown(self):
        r = delete_account(username)
        self.assertIn(r.status_code, [204, 404], "Account cannot be deleted")

    def test_new_account_json(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test"}
        r = post_json("/accounts/", payload, headers={"NGV-Signup-Code": "RYEDc9zq"})
        self.assertEqual(r.status_code, 201, "Account cannot be created with JSON body")

    def test_new_account_formencoded(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test", "signup_code": "RYEDc9zq"}
        r = post_url_encoded("/accounts/", payload)
        self.assertEqual(r.status_code, 201, "Account cannot be created with form-encoded body")

    def test_new_account_redirect_success(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test", "signup_code": "RYEDc9zq"}
        r = post_url_encoded("/accounts/?onsuccess=%2Fs&onfailure=%2Ff", payload)
        self.assertEqual(r.status_code, 302, "Account creation redirection request does not redirect")
        self.assertRegex(r.headers['location'], re.compile('^/s(\?.+)?'), "Account creation redirection request does not redirect to the onsuccess URL")

    def test_new_account_redirect_failure(self):
        payload = {}
        r = post_url_encoded("/accounts/?onsuccess=%2Fs&onfailure=%2Ff", payload)
        self.assertEqual(r.status_code, 302, "Account creation redirection request does not redirect")
        self.assertRegex(r.headers['location'], re.compile('^/f(\?.+)?'), "Account creation redirection request does not redirect to the onfailure URL")

    def test_new_account_redirect_formdata(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test", "signup_code": "RYEDc9zq", "onsuccess": "/s", "onfailure": "/f"}
        r = post_url_encoded("/accounts/", payload)
        self.assertEqual(r.status_code, 302, "Account creation redirection request does not redirect when onsuccess/onfailure are in the form-encoded body, not the URL")
        
    def test_new_account_conflict(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test"}
        r = post_json("/accounts/", payload, headers={"NGV-Signup-Code": "RYEDc9zq"})
        r = post_json("/accounts/", payload, headers={"NGV-Signup-Code": "RYEDc9zq"})
        self.assertEqual(r.status_code, 409, "Double account creation does not return 409 Conflict")

class LoginTest(unittest.TestCase):
    def setUp(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test"}
        r = post_json("/accounts/", payload, headers={"NGV-Signup-Code": "RYEDc9zq"})
        self.assertEqual(r.status_code, 201, "Account cannot be created with JSON body")
        self.payload = {"username": username, "password": "Please enter your details"}
        self.invalid_payload = {"username": username, "password": "a"}

    def tearDown(self):
        r = delete_account(username)
        self.assertEqual(r.status_code, 204, "Account cannot be deleted")

    def test_login_json(self):
        r = post_json("/session/", self.payload)
        self.assertEqual(r.status_code, 201, "Cannot log in with JSON body")
        self.assertIn('username', r.cookies, "Login response does not contain secure cookie")

    def test_login_formencoded(self):
        r = post_url_encoded("/session/", self.payload)
        self.assertEqual(r.status_code, 201, "Cannot log in with form-encoded body")
        self.assertIn('username', r.cookies, "Login response does not contain secure cookie")

    def test_login_redirect_success(self):
        r = post_url_encoded("/session/?onsuccess=%2Fs&onfailure=%2Ff", self.payload)
        self.assertEqual(r.status_code, 302, "Login redirection request does not redirect")
        self.assertRegex(r.headers['location'], re.compile('^/s(\?.+)?'), "Account creation redirection request does not redirect to the onsuccess URL")
        self.assertIn('username', r.cookies, "Login response does not contain secure cookie")

    def test_login_redirect_failure(self):
        payload = {}
        r = post_url_encoded("/session/?onsuccess=%2Fs&onfailure=%2Ff", payload)
        self.assertEqual(r.status_code, 302, "Login redirection request does not redirect")
        self.assertRegex(r.headers['location'], re.compile('^/f(\?.+)?'), "Account creation redirection request does not redirect to the onfailure URL")
        self.assertNotIn('username', r.cookies, "Failed login response does contains secure cookie")

    def test_login_forbidden(self):
        r = post_url_encoded("/session/", self.invalid_payload)
        self.assertEqual(r.status_code, 403, "Invalid login does not return 403 Forbidden")
        self.assertNotIn('username', r.cookies, "Failed login response does contains secure cookie")

    def test_login_redirect_formdata(self):
        r = post_url_encoded("/session/", self.payload)
        self.assertEqual(r.status_code, 302, "Login redirection request does not redirect when onsuccess/onfailure are in the form-encoded body, not the URL")
        self.assertIn('username', r.cookies, "Login response does not contain secure cookie")

class TestWithAccount(unittest.TestCase):
    def setUp(self):
        payload = {"username": username, "password": "Please enter your details", "email": username, "full_name": "Ellis API Test"}
        r = post_json("/accounts/", payload, headers={"NGV-Signup-Code": "RYEDc9zq"})
        self.assertEqual(r.status_code, 201, "Account cannot be created with JSON body")
        payload = {"username": username, "password": "Please enter your details"}
        r = post_json("/session/", payload)
        self.assertEqual(r.status_code, 201, "Cannot log in with JSON body")
        self.session_cookies = r.cookies

    def tearDown(self):
        r = delete_account(username)
        self.assertEqual(r.status_code, 204, "Account cannot be deleted")

class NumberCreationTest(TestWithAccount):
    def check_valid_number_response(self, json, expect_gab=True, expect_password=True, expect_pstn=True):
        self.assertIn('formatted_number', json)
#       if expect_gab:
#            self.assertIn('gab_listed', json)
        self.assertIn('number', json)
        if expect_pstn:    
            self.assertIn('pstn', json)    
        self.assertIn('private_id', json)
        if expect_password:
            self.assertIn('sip_password', json)    
        self.assertIn('sip_uri', json)    
        self.assertIn('sip_username', json)
        self.assertEqual(json['number'], json['sip_username'])

    def test_create_from_pool(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.check_valid_number_response(r.json())
        self.assertIs(r.json()['pstn'], False)

    def test_create_pstn_from_pool(self):
        payload = {"pstn": "true"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.assertTrue(((r.status_code >= 200) and (r.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r.json(), expect_gab=False)
        self.assertIs(r.json()['pstn'], True)

    def test_create_pstn_json(self):
        payload = {"pstn": "true"}
        r = post_json("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.assertTrue(((r.status_code >= 200) and (r.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r.json(), expect_gab=False)
        self.assertIs(r.json()['pstn'], True)

    def test_create_pstn_queryp(self):
        payload = {"pstn": "true"}
        r = post_query_params("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.assertTrue(((r.status_code >= 200) and (r.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r.json(), expect_gab=False)
        self.assertIs(r.json()['pstn'], True)

    def test_create_with_existing_impi(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.assertTrue(((r.status_code >= 200) and (r.status_code < 300)), "Account creation did not return a 2xx response")
        payload = {"pstn": "false", "private_id": r.json()['private_id']}
        r2 = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        self.check_valid_number_response(r2.json(), expect_password=False)
        self.assertTrue(((r2.status_code >= 200) and (r2.status_code < 300)), "Account creation did not return a 2xx response")
        self.assertEqual(r2.json()['private_id'], r.json()['private_id'])

    def test_create_specific(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, headers={"NGV-API-Key": api_key})
        self.assertTrue(((r.status_code >= 200) and (r.status_code < 300)), "Account creation did not return a 2xx response")
        payload = {"private_id": r.json()['private_id']}
        r2 = post_url_encoded("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        self.check_valid_number_response(r2.json(), expect_password=False, expect_pstn=False)
        self.assertTrue(((r2.status_code >= 200) and (r2.status_code < 300)), "Account creation did not return a 2xx response")
        self.assertEqual(r2.json()['private_id'], r.json()['private_id'])
        self.assertEqual(r2.json()['number'], '12345')
        self.assertEqual(r2.json()['sip_username'], '12345')
        self.assertEqual(r2.json()['sip_uri'], 'sip:12345@staging.cw-ngv.com')

    def test_create_specific_newimpi(self):
        payload = {"private_id": "rkd@rkd.me.uk", "new_private_id": "true"}
        r2 = post_url_encoded("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        self.assertTrue(((r2.status_code >= 200) and (r2.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r2.json(), expect_password=True, expect_pstn=False)
        self.assertEqual(r2.json()['private_id'], "rkd@rkd.me.uk")
        self.assertEqual(r2.json()['number'], '12345')
        self.assertEqual(r2.json()['sip_username'], '12345')
        self.assertEqual(r2.json()['sip_uri'], 'sip:12345@staging.cw-ngv.com')

    def test_create_specific_newimpi_json(self):
        payload = {"private_id": "rkd@rkd.me.uk", "new_private_id": "true"}
        r2 = post_json("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        self.assertTrue(((r2.status_code >= 200) and (r2.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r2.json(), expect_password=True, expect_pstn=False)
        self.assertEqual(r2.json()['private_id'], "rkd@rkd.me.uk")
        self.assertEqual(r2.json()['number'], '12345')
        self.assertEqual(r2.json()['sip_username'], '12345')
        self.assertEqual(r2.json()['sip_uri'], 'sip:12345@staging.cw-ngv.com')

    def test_create_specific_newimpi_queryp(self):
        payload = {"private_id": "rkd@rkd.me.uk", "new_private_id": "true"}
        r2 = post_query_params("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        self.assertTrue(((r2.status_code >= 200) and (r2.status_code < 300)), "Account creation did not return a 2xx response")
        self.check_valid_number_response(r2.json(), expect_password=True, expect_pstn=False)
        self.assertEqual(r2.json()['private_id'], "rkd@rkd.me.uk")
        self.assertEqual(r2.json()['number'], '12345')
        self.assertEqual(r2.json()['sip_username'], '12345')
        self.assertEqual(r2.json()['sip_uri'], 'sip:12345@staging.cw-ngv.com')

class NumberManagementTest(TestWithAccount):
    def test_get_numbers(self):
        r = requests.get("{}/accounts/{}/numbers/".format(where, username), cookies=self.session_cookies)
        self.assertIn('numbers', r.json())
        self.assertEqual(0, len(r.json()['numbers']))
        payload = {"pstn": "false"}
        post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        payload = {"private_id": "rkd@rkd.me.uk", "new_private_id": "true"}
        post_query_params("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        r = requests.get("{}/accounts/{}/numbers/".format(where, username), cookies=self.session_cookies)
        self.assertIn('numbers', r.json())
        self.assertEqual(2, len(r.json()['numbers']))

    def test_get_numbers_after_deletion(self):
        r = requests.get("{}/accounts/{}/numbers/".format(where, username), cookies=self.session_cookies)
        self.assertIn('numbers', r.json())
        self.assertEqual(0, len(r.json()['numbers']))
        payload = {"pstn": "false"}
        post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        payload = {"private_id": "rkd@rkd.me.uk", "new_private_id": "true"}
        post_query_params("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), payload, headers={"NGV-API-Key": api_key})
        r = requests.get("{}/accounts/{}/numbers/".format(where, username), cookies=self.session_cookies)
        self.assertIn('numbers', r.json())
        self.assertEqual(2, len(r.json()['numbers']))
        delete("/accounts/{}/numbers/sip:12345@staging.cw-ngv.com".format(username), headers={"NGV-API-Key": api_key})
        r = requests.get("{}/accounts/{}/numbers/".format(where, username), cookies=self.session_cookies)
        self.assertIn('numbers', r.json())
        self.assertEqual(1, len(r.json()['numbers']))

    def test_change_password(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        original_password = r.json()['sip_password']
        uri = r.json()['sip_uri']
        r = post_url_encoded("/accounts/{}/numbers/{}/password".format(username, uri), {}, cookies=self.session_cookies)
        new_password = r.json()['sip_password']
        self.assertNotEqual(original_password, new_password)

class GlobalAddressBookTest(TestWithAccount):
    def test_get_gab(self):
        r = get("/gab/", cookies=self.session_cookies)
        self.assertEqual(r.status_code, 200)
        self.assertIn('contacts', r.json())

    def test_add_number_to_gab(self):
        r = get("/gab/", cookies=self.session_cookies)
        self.assertEqual(0, len(list(filter(lambda x: x['email'] == username, r.json()['contacts']))), "User appears in the GAB even with no numbers")
        payload = {"pstn": "false"}
        post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        r = get("/gab/", cookies=self.session_cookies)
        my_numbers = list(filter(lambda x: x['email'] == username, r.json()['contacts']))[0]['numbers']
        self.assertEqual(1, len(my_numbers))
        
    def test_toggle_gab(self):
        r = get("/gab/", cookies=self.session_cookies)
        self.assertEqual(0, len(list(filter(lambda x: x['email'] == username, r.json()['contacts']))), "User appears in the GAB even with no numbers")

        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        uri = r.json()['sip_uri']

        r = get("/gab/", cookies=self.session_cookies)
        my_numbers = list(filter(lambda x: x['email'] == username, r.json()['contacts']))[0]['numbers']
        self.assertEqual(1, len(my_numbers))

        put("/accounts/{}/numbers/{}/listed/0".format(username, uri), {}, cookies=self.session_cookies)
        r = get("/gab/", cookies=self.session_cookies)
        self.assertEqual(0, len(list(filter(lambda x: x['email'] == username, r.json()['contacts']))), "User appears in the GAB even after unlisting all numbers")

        put("/accounts/{}/numbers/{}/listed/1".format(username, uri), {}, cookies=self.session_cookies)
        r = get("/gab/", cookies=self.session_cookies)
        my_numbers = list(filter(lambda x: x['email'] == username, r.json()['contacts']))[0]['numbers']
        self.assertEqual(1, len(my_numbers))
        


class IFCsTest(TestWithAccount):
    def test_change_ifcs(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        uri = r.json()['sip_uri']
        r = get("/accounts/{}/numbers/{}/ifcs".format(username, uri), cookies=self.session_cookies)
        old_ifcs = r.text
        new_ifcs = '<?xml version="1.0" encoding="UTF-8"?><ServiceProfile><InitialFilterCriteria><TriggerPoint><ConditionTypeCNF>0</ConditionTypeCNF><SPT><ConditionNegated>0</ConditionNegated><Group>0</Group><Method>INVITE</Method><Extension></Extension></SPT></TriggerPoint><ApplicationServer><ServerName>sip:differentas.staging.cw-ngv.com</ServerName><DefaultHandling>0</DefaultHandling></ApplicationServer></InitialFilterCriteria></ServiceProfile>'
        r = put("/accounts/{}/numbers/{}/ifcs".format(username, uri), new_ifcs, cookies=self.session_cookies)
        self.assertEqual(r.status_code, 200)
        r = get("/accounts/{}/numbers/{}/ifcs".format(username, uri), cookies=self.session_cookies)
        self.maxDiff = None
        self.assertEqual(r.text, new_ifcs)
        self.assertNotEqual(r.text, old_ifcs)

        
class SimservsTest(TestWithAccount):
    def test_change_simservs(self):
        payload = {"pstn": "false"}
        r = post_url_encoded("/accounts/{}/numbers/".format(username), payload, cookies=self.session_cookies)
        uri = r.json()['sip_uri']
        r = get("/accounts/{}/numbers/{}/simservs".format(username, uri), cookies=self.session_cookies)
        old_simservs = r.text
        new_simservs = '<?xml version="1.0" encoding="UTF-8"?><simservs xmlns="http://uri.etsi.org/ngn/params/xml/simservs/xcap" xmlns:cp="urn:ietf:params:xml:ns:common-policy"><originating-identity-presentation active="true"/><originating-identity-presentation-restriction active="true"><default-behaviour>presentation-not-restricted</default-behaviour></originating-identity-presentation-restriction><communication-diversion active="true"><NoReplyTimer>29</NoReplyTimer><cp:ruleset/></communication-diversion><incoming-communication-barring active="true"><cp:ruleset><cp:rule id="rule0"><cp:conditions/><cp:actions><allow>true</allow></cp:actions></cp:rule></cp:ruleset></incoming-communication-barring><outgoing-communication-barring active="true"><cp:ruleset><cp:rule id="rule0"><cp:conditions/><cp:actions><allow>true</allow></cp:actions></cp:rule></cp:ruleset></outgoing-communication-barring></simservs>'
        r = put("/accounts/{}/numbers/{}/simservs".format(username, uri), new_simservs, cookies=self.session_cookies)
        self.assertEqual(r.status_code, 200)
        r = get("/accounts/{}/numbers/{}/simservs".format(username, uri), cookies=self.session_cookies)
        self.maxDiff = None
        self.assertEqual(r.text, new_simservs)
        self.assertNotEqual(r.text, old_simservs)
