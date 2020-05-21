from flask import Flask, render_template, request, make_response, jsonify
import re
import datetime
import logging.config
import json
import uuid
from flask_table import Table, Col
# import db_helper
import os
import ast
import yaml
import secrets

app = Flask(__name__)
ACCOUNT = 5

logger = logging.getLogger('RingRing')
logger.setLevel(logging.INFO)

class InvoiceFilter():
    def filter(self, logRecord):
        return logRecord.levelno == ACCOUNT

def get_invoice_controller(log_level='ACCOUNT'):
    with open('InvoiceApp/logger-config.yml', 'r') as yaml_file:
        config = yaml_file.read().format(level=log_level)
        config = yaml.load(config, Loader=yaml.Loader)
        logging.addLevelName(ACCOUNT, 'ACCOUNT')
        logging.config.dictConfig(config)
        logging.Logger.account = account
        logger = logging.getLogger('invoice_controller')
    return logger
    # return logging.LoggerAdapter(logger, extra)

def account(self, msg, *args, **kwargs):
    if self.isEnabledFor(ACCOUNT):
        self._log(ACCOUNT, msg, args, **kwargs)

@app.route("/")
def home():
    log_level = request.args.get('log-level')
    print(log_level)
    controller = get_invoice_controller(log_level)
    controller.info('Testing logger.')

    response = make_response(render_template("logs.html", table=''))

    # if not request.cookies.get('session_id'):
    #     # TODO is uuid safe or rather use hash?
    #     session_id = str(uuid.uuid4())
    #     response.set_cookie('session_id', session_id)
    #     db_helper.add_session(session_id)

    return response


@app.route("/request-bill")
def request_bill():
    guest_name = request.args.get('name')
    bill = []
    total = 0.0
    with open('InvoiceApp/invoices/accounting.log') as journal:
        for entry in journal:
            invoice = json.loads(entry)
            print(invoice)
            if invoice['name'] == guest_name:
                bill.append(invoice)
                total += float(invoice['amount'])
    # total = sum(bill, 'amount')
    return jsonify(total=total, items=bill, success=True)

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

def validate_invoice(guest_name, invoice_item):
    return guest_name and invoice_item

def get_price(item):
    return 9.99

def get_invoice_number():
    return secrets.randbits(32)

def storno():
    print()

def start_app():
    app.run(port=7354, host='127.0.0.1', threaded=True)

if __name__ == "__main__":
    app.run(port=7354, host='0.0.0.0')
