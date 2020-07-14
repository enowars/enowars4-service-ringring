FROM python:3.8.1

COPY InvoiceApp /InvoiceApp
RUN pip3 install -r /InvoiceApp/requirements.txt

RUN apt-get update && \
    apt-get -y install netcat

RUN chmod 0666 /InvoiceApp/accounting/*

RUN echo "root:$(openssl rand -hex 20)" | chpasswd
RUN useradd -m hotelguest && \
    echo "hotelguest:$(openssl rand -hex 20)" | chpasswd
USER hotelguest

WORKDIR /InvoiceApp
EXPOSE 7354
ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "app:app" ]