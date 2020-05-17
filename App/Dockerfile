FROM python:3.8.1

LABEL version="0.0.1"

ENV FLASK_APP "app.py"
# ENV FLASK_DEBUG True

RUN mkdir /service-ringring
WORKDIR /service-ringring

#COPY Pip* /service-ringring/

ADD . /service-ringring

RUN pip install --upgrade pip && \
    pip install -r /service-ringring/requirements.txt
#    pip install pipenv && \
#    pipenv install -r /service-ringring/requirements.txt
#    pipenv install --dev --system --deploy --ignore-pipfile


#CMD flask run --host=0.0.0.0 --port=7353
CMD ["python", "app.py"]

EXPOSE 7353
