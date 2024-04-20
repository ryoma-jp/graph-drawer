FROM python:3.8

ARG UID

RUN groupadd -g ${UID} app_user && \
    useradd -m -s /bin/bash -u ${UID} -g ${UID} app_user

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./app /app

CMD ["uwsgi", "--uid", "app_user", "--ini", "app.ini"]
