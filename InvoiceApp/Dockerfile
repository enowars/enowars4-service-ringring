FROM python:3.8.1
LABEL version="0.0.1"

COPY InvoiceApp /InvoiceApp
# WORKDIR /InvoiceApp

RUN pip install --upgrade pip && \
    pip install -r /InvoiceApp/requirements.txt

ENTRYPOINT ["python", "/InvoiceApp/app.py"]

EXPOSE 7354
