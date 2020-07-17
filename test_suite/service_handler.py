import requests
import logging
import grequests
import sys

BASE_URL = "http://localhost:7353"
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def init_user():
    session = requests.Session()
    session.cookies.set('session_id', None)
    request = grequests.get(BASE_URL, session=session)
    return request, session

def make_vip(session):
    request = grequests.post(f"{BASE_URL}/make_me_a_vip", session = session)
    return request
def call_bot_response(payload, session):
    request = grequests.get(f"{BASE_URL}/get_bot_response", params=payload, session = session)
    return request

def get_invoices(session):
    request = grequests.get(f"{BASE_URL}/invoices", session = session)
    return request

