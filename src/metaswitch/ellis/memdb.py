__author__ = 'rkd'
from .db import Database

class InMemoryDatabase(Database):
    def __init__(self):
        self.users = {}

    def save_user(self, user):
        self.users[user.email] = user

    def get_user(self, email):
        return self.users.get(email)

    def get_next_free_line(self):
        return "sip:1234@example.com"