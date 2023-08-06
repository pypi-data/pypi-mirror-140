import os

from pypirepo.login import *

this_dir = os.path.dirname(os.path.abspath(__file__))


def test_produce_login():
    print()
    os.environ['HOME'] = this_dir
    login = produce_login()
    print(login)
    assert login.username == 'test-user'
    assert login.password == 'test-pass'
