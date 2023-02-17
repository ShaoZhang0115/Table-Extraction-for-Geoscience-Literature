FROM python:3.9-buster as REQUIREMENTS_BUILDER

WORKDIR /

RUN set -ex;  \
    pip install pipenv==2022.1.8 -i https://mirrors.aliyun.com/pypi/simple

COPY Pipfile /

RUN set -ex ;\
    sed -i -Ee "s/^(.*git.acemap.cn.*)$/#\1/g" Pipfile ;\
    pipenv lock -r >/requirements.txt ;\
    grep git.acemap.cn Pipfile | sed -Ee "s/^.*(https:\/\/.*git.acemap.cn.*)\/(.*?).git.*ref.*\"([0123456789.]+)\".*$/git+\1\/\2.git#egg=\2==\3/g" >>/requirements.txt


FROM python:3.9-buster

WORKDIR /app

RUN set -ex; \
    sed -i 's#http://deb.debian.org#https://mirrors.aliyun.com#g' /etc/apt/sources.list; \
    apt update; \
    apt install -y --no-install-recommends curl libgl1-mesa-glx libglib2.0-dev libleptonica-dev; \
    rm -rf /var/lib/apt/lists/*

COPY --from=REQUIREMENTS_BUILDER /requirements.txt .

RUN set -ex; \
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

COPY . /app

ENV PYTHONPATH=$PYTHONPATH:/app

LABEL project="table-open-source-backend"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
