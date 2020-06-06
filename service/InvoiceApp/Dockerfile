FROM python:3.8.1
LABEL version="0.0.1"

COPY InvoiceApp /InvoiceApp
WORKDIR /InvoiceApp

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 7354

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "app:app" ]
