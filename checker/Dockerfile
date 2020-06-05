FROM python:3
#RUN pip install git+https://github.com/domenukk/enochecker
RUN apt-get update
RUN apt-get install -y git

COPY . .
WORKDIR .
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "checker:app" ]
