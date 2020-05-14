FROM python:3.8.1

LABEL version="0.0.1"

ENV FLASK_APP "app.py"
# ENV FLASK_DEBUG True

RUN mkdir /service-ringring
WORKDIR /service-ringring

COPY Pip* /service-ringring/

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --dev --system --deploy --ignore-pipfile

ADD . /service-ringring

CMD flask run --host=0.0.0.0
