from flask import Flask, render_template, request, make_response, jsonify
from flask_table import Table, Col
from pathlib import Path
import logging.config
import secrets
import yaml
import json

app = Flask(__name__)
ACCOUNT = 5

logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)

class InvoiceItemTable(Table):
    invoice_number = Col('Invoice Number')
    item = Col('Item')
    name = Col('Guest Name')
    amount = Col('Amount')
    note = Col('Note')

class InvoiceFilter():
    def filter(self, logRecord):
        return logRecord.levelno == ACCOUNT

@app.route("/")
def home():
    log_level = request.args.get('log-level', 'DEBUG')
    controller = get_invoice_controller(log_level)
    controller.info('log_level')
    guest_name = request.args.get('name')

    guest_invoices = []
    if guest_name:
        controller.info(f"Generating invoice overview for guest '{guest_name}'...")
        guest_invoices = get_accounted_invoices(guest_name)

    return make_response(render_template("logs.html", table=InvoiceItemTable(guest_invoices)))

    # if not request.cookies.get('session_id'):
    #     # TODO is uuid safe or rather use hash?
    #     session_id = str(uuid.uuid4())
    #     response.set_cookie('session_id', session_id)
    #     db_helper.add_session(session_id)

@app.route("/add")
def add_to_bill():
    guest_name = request.args.get('name')
    invoice_item = request.args.get('item')
    note = request.args.get('note', '')

    if not validate_invoice(guest_name, invoice_item):
        logger.warning(f"Aborting invoice accounting - invoice parameters guest name '{guest_name}' and item '{invoice_item}' are not valid (HTTP 404).")
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

    controller = get_invoice_controller()
    controller.account(f'invoice #{invoice_number} accounted', extra=invoice)
    return jsonify(success=True)

@app.route("/storno")
def storno():
    controller = get_invoice_controller()
    invoice_number = request.args.get('number')
    for invoice in accounted_invoices():
        if invoice['invoice_number'] == invoice_number:
            # creating storno invoice number
            invoice['invoice_number'] = get_invoice_number()
            invoice['amount'] = float(invoice['amount']) * -1
            invoice['guest_name'] = invoice.pop('name')
            invoice.pop('time')
            controller.account(f"cancelling invoice #{invoice_number} (negative booking #{invoice['invoice_number']})", extra=invoice)
            return jsonify(success=True)

    logger.warning(f"cancelling invoice failed - no invoice found for invoice number '{invoice_number}' (HTTP 404).")
    return jsonify(success=False), 404

@app.route("/request-bill")
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
    return 9.99

def get_invoice_number():
    return secrets.randbits(32)

def accounted_invoices(guest_name=None):
    log = Path('InvoiceApp/invoices/accounting.log')
    if not log.is_file():
        return

    with log.open() as journal:
        for entry in journal:
            invoice = json.loads(entry)
            if not guest_name or invoice['name'] == guest_name:
                yield invoice

def get_accounted_invoices(guest_name=None):
    return list(accounted_invoices(guest_name))

def get_invoice_controller(log_level='ACCOUNT'):
    with open('InvoiceApp/logger-config.yml', 'r') as yaml_file:
        config = yaml_file.read().format(level=log_level)
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

if __name__ == "__main__":
    start_app(host='0.0.0.0')
