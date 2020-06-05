import logging
import requests
import hashlib
import os

PAYMENT_ON_ACCOUNT = 'room-bill'


def add_to_invoice(guest_name, service, payment_method=PAYMENT_ON_ACCOUNT, notes=None):
    if 'INVOICE_HOST' not in os.environ:
        logger = logging.getLogger('RingRing')
        logger.error(f'Could not create invoice for {service} for {guest_name}. INVOICE_HOST variabe is missing.')
        return

    guest_pseudonym = hashlib.md5(guest_name.encode('utf-8')).hexdigest()
    url = 'http://' + os.environ['INVOICE_HOST'] + ':7354/add'
    params = {'name': guest_pseudonym, 'item': service, 'payment': payment_method, 'note': notes}
    requests.post(url, params)


def get_invoices(guest_name):
    logger = logging.getLogger('RingRing')
    if 'INVOICE_HOST' not in os.environ:
        logger.error(f"Could not get invoice for '{guest_name}''. INVOICE_HOST variabe is missing.")
        return []
    if not guest_name:
        logger.warning(f"Abort getting invoice overview - mandatory parameter guest name '{guest_name}' is not set.")
        return []

    guest_pseudonym = hashlib.md5(guest_name.encode('utf-8')).hexdigest()
    url = 'http://' + os.environ['INVOICE_HOST'] + ':7354/'
    response = requests.get(url, {'name': guest_pseudonym})

    if response.status_code != 200:
        return []

    invoices = response.json()['invoices']
    for invoice in invoices:
        invoice['name'] = guest_name
        invoice.pop('note')

    return invoices


def request_bill(guest_name):
    logger = logging.getLogger('RingRing')
    if 'INVOICE_HOST' not in os.environ:
        logger.error(f"Could not get invoice for '{guest_name}''. INVOICE_HOST variabe is missing.")
        return []
    if not guest_name:
        logger.warning(f"Abort getting invoice overview - mandatory parameter guest name '{guest_name}' is not set.")
        return []
    guest_pseudonym = hashlib.md5(guest_name.encode('utf-8')).hexdigest()
    url = 'http://' + os.environ['INVOICE_HOST'] + ':7354/request-bill'
    response = requests.get(url, {'name': guest_pseudonym})
    data = response.json()
    return data['items'], data['total']
