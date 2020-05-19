FROM python:3.8.1
LABEL version="0.0.1"

RUN mkdir /service-ringring
WORKDIR /service-ringring
COPY . /service-ringring

RUN pip install --upgrade pip && \
    pip install -r /service-ringring/App/requirements.txt

ENTRYPOINT ["python", "App/app.py"]

EXPOSE 7353
