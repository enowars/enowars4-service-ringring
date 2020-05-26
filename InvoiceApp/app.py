from flask import Flask, render_template, request, redirect, make_response, jsonify
from flask_table import Table, Col
from urllib.parse import urlparse
from pathlib import Path
import logging.config
import secrets
import yaml
import json

app = Flask(__name__)
ACCOUNT = 5
PAYMENT_ON_ACCOUNT = 'room-bill'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InvoiceFilter:
    def __init__(self, payment_method, invoice_status):
        self.payment_method = payment_method
        self.invoice_status = invoice_status

    def get_invoice_status(self, payment_method):
        if payment_method == 'cash' or payment_method == 'debit':
            return 'settled'
        else:
            return 'outstanding'

    def filter(self, logRecord):
        return logRecord.levelno == ACCOUNT and self.get_invoice_status(self.payment_method) == self.invoice_status


@app.route('/')
def home():
    guest_name = request.args.get('name')
    log_level = request.args.get('log-level', 'DEBUG')
    controller = get_invoice_controller(log_level=log_level)
    controller.info('log_level')

    if not guest_name:
        logger.warning(
            f"Abort getting invoice overview - mandatory parameter guest name '{guest_name}' is not set (HTTP 404).")
        return jsonify(success=False), 404

    controller.info(f"Generating invoice overview for guest '{guest_name}'...")
    guest_invoices = get_accounted_invoices(guest_name=guest_name, include_settled=True)
    return jsonify(invoices=guest_invoices, success=True)


@app.route('/add', methods=['POST'])
def add_to_bill():
    guest_name = request.form.get('name')
    invoice_item = request.form.get('item')
    payment_method = request.form.get('payment-method', PAYMENT_ON_ACCOUNT)
    note = request.form.get('note', '')

    if not validate_invoice(guest_name, invoice_item):
        logger.warning(
            f"Aborting invoice accounting - invoice parameters guest name '{guest_name}' and item '{invoice_item}' are not valid (HTTP 404).")
        return jsonify(success=False), 404

    amount = get_price(invoice_item)
    invoice_number = get_invoice_number()
    invoice = {
        'invoice_number': invoice_number,
        'item': invoice_item,
        'guest_name': guest_name,
        'amount': amount,
        'note': note
    }

    controller = get_invoice_controller(payment_method=payment_method)
    controller.account(f'invoice #{invoice_number} accounted', extra=invoice)
    return jsonify(success=True)


@app.route('/storno', methods=['POST'])
def storno():
    controller = get_invoice_controller()
    invoice_number = request.form.get('number')
    for invoice in accounted_invoices():
        if invoice['invoice_number'] == invoice_number:
            # creating storno invoice number
            invoice['invoice_number'] = get_invoice_number()
            invoice['amount'] = float(invoice['amount']) * -1
            invoice['guest_name'] = invoice.pop('name')
            invoice.pop('time')
            controller.account(f"cancelling invoice #{invoice_number} (negative booking #{invoice['invoice_number']})",
                               extra=invoice)
            return jsonify(success=True)

    logger.warning(f"cancelling invoice failed - no invoice found for invoice number '{invoice_number}' (HTTP 404).")
    return jsonify(success=False), 404


@app.route('/request-bill')
def request_bill():
    guest_name = request.args.get('name')
    logger.info(f"Requesting bill for guest '{guest_name}'...")
    if not guest_name:
        logger.warning(f"Aborting bill request - parameter guest name '{guest_name}' is not valid (HTTP 404).")
        return jsonify(success=False), 404

    bill = []
    total = 0.0
    for invoice in accounted_invoices(guest_name):
        bill.append(invoice)
        total += float(invoice['amount'])
    return jsonify(total=total, items=bill, success=True)


def validate_invoice(guest_name, invoice_item):
    return guest_name and invoice_item


def get_price(item):
    price_sheet = {
        'alarm': 1.50,
        'pizza': 6.00,
        'wine': 4.00,
        'room-service-food': 9.99,
        'reception': 0.0,
        'extra-cleaning': 20.0
    }
    return price_sheet.get(item, None)


def get_invoice_number():
    return secrets.randbits(32)


def accounted_invoices(guest_name=None, file_path='InvoiceApp/accounting/outstanding-invoices.log'):
    if not Path(file_path).is_file():
        return

    with open(file_path) as journal:
        for entry in journal:
            invoice = json.loads(entry)
            if not guest_name or invoice['name'] == guest_name:
                yield invoice


def get_accounted_invoices(guest_name=None, include_settled=False):
    invoices = list(accounted_invoices(guest_name=guest_name))
    if include_settled:
        invoices.extend(
            accounted_invoices(guest_name=guest_name, file_path='InvoiceApp/accounting/settled-invoices.log'))
    return invoices


def get_invoice_controller(payment_method=PAYMENT_ON_ACCOUNT, log_level='ACCOUNT'):
    with open('InvoiceApp/logger-config.yml', 'r') as yaml_file:
        config = yaml_file.read().format(payment_method=payment_method, level=log_level)
        config = yaml.load(config, Loader=yaml.Loader)
        logging.addLevelName(ACCOUNT, 'ACCOUNT')
        logging.config.dictConfig(config)
        logging.Logger.account = account
        logger = logging.getLogger('invoice_controller')
        logger.debug('invoice-controller logger started.')
    return logger


def account(self, msg, *args, **kwargs):
    if self.isEnabledFor(ACCOUNT):
        self._log(ACCOUNT, msg, args, **kwargs)


def start_app(host, threaded=False):
    app.run(port=7354, host=host, threaded=threaded)


if __name__ == '__main__':
    start_app(host='0.0.0.0')
