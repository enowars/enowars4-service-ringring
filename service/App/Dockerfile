FROM python:3.8.1
LABEL version="0.0.1"

COPY service/App /service-ringring
WORKDIR /service-ringring

RUN pip install --upgrade pip && \
    pip install -r /service-ringring/requirements.txt

ENTRYPOINT ["python", "/service-ringring/app.py"]

EXPOSE 7353
