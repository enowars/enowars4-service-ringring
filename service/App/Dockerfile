FROM python:3.8.1
LABEL version="0.0.1"

COPY App /service-ringring
WORKDIR /service-ringring

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 7353

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "app:app" ]
