from flask import request
import functools
import logging
import requests
import hashlib
import os


def debug(_func=None, *, _debug=False, _args_kwargs=True, _returned_value=True, logger=logging.getLogger()):
    def decorator_debug(func):
        @functools.wraps(func)
        def wrapper_debug(*args, **kwargs):
            _debug = request.args.get('debug')
            if _debug == 'True':
                signature = ''
                if _args_kwargs:
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]
                    signature = ', '.join(args_repr + kwargs_repr)
                    logger.setLevel(logging.DEBUG)
                    logger.debug(f'Calling {func.__name__}({signature})')
                else:
                    logger.debug(f'Calling {func.__name__}')

            value = func(*args, **kwargs)

            if _debug == 'True':
                if _returned_value:
                    logger.debug(f'{func.__name__!r} returned {value!r}')
            return value

        return wrapper_debug

    if _func is None:
        return decorator_debug
    else:
        return decorator_debug(_func)


def add_to_invoice(guest_name, service):
    if 'INVOICE_HOST' not in os.environ:
        logger = logging.getLogger('RingRing')
        logger.error(f'Could not create invoice for {service} for {guest_name}. INVOICE_HOST variabe is missing.')
        return

    guest_pseudonym = hashlib.md5(guest_name.encode('utf-8')).hexdigest()
    url = 'http://' + os.environ['INVOICE_HOST'] + ':7354/add'
    params = {'name': guest_pseudonym, 'item': service}
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

    return invoices
