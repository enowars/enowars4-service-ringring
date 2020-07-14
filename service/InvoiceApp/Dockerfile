FROM python:3.8.1
LABEL version="0.0.1"

COPY InvoiceApp/requirements.txt /InvoiceApp/
RUN pip3 install -r /InvoiceApp/requirements.txt

COPY InvoiceApp /InvoiceApp
WORKDIR /InvoiceApp

EXPOSE 7354

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "app:app" ]
