import requests
import json
import os

URL = "http://localhost:7354"


def test_invoice_overview():
    params = {'name': 'do-not-exist'}
    r = requests.get(URL, params)
    assert r.status_code == 200
    assert len(r.json()['invoices']) == 0


def test_invoice_overview_error_handling():
    r = requests.get(URL)
    assert r.status_code == 404



# params = {'name': 'somebody", "time": "2020-05-29 00:12:15,799", "amount": "6.0", "note": ""}', 'item': 'pizza'}
# params = {'name': 'somebody', 'item': 'pizza', 'note': 'foo"}\n{"test": {"test": '}
# params = {'name': 'somebody', 'item': 'pizza', 'note': 'foo"}\n{"test": {"test": /\\'}
# params = {'name': 'somebody', 'item': 'pizza', 'note': 'foo"}\n{"test": {'}
params = {'name': 'somebody', 'item': os.urandom(10000000)}

r = requests.post(URL + '/add', params)
print(r.status_code)
print(r.text)