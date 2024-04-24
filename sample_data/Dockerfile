FROM python:3.8

ARG UID

RUN groupadd -g ${UID} app_user && \
    useradd -m -s /bin/bash -u ${UID} -g ${UID} app_user

WORKDIR /sample_data

COPY ./requirements.txt /sample_data/requirements.txt

RUN pip install -r requirements.txt

COPY . /sample_data

CMD ["bash"]
