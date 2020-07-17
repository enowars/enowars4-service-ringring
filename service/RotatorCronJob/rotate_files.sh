#!/usr/bin/env bash

mv /InvoiceApp/accounting/outstanding-invoices.log /InvoiceApp/accounting/outstanding-invoices.log.$(date +%d-%m-%Y-%H-%M-%S)
echo "File rotated."
