FROM python:3.7.4-buster as whirlpool-due-base

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends netcat \
  && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash whirlpool

ARG WH_DUE_ROOT=/home/whirlpool/whirlpool-due
WORKDIR $WH_DUE_ROOT

RUN chown -R whirlpool:whirlpool $WH_DUE_ROOT

# files necessary to build the project
COPY .pylintrc ./
COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY scripts/ scripts/
COPY logs/ logs/
COPY urlfilter/ urlfilter/

# docker image for dev target
FROM whirlpool-due-base as whirlpool-due-dev

COPY scripts/wait-for-it.sh scripts/wait-for-it.sh
ENTRYPOINT ["bash ./scripts/wait-for-it.sh"]

# docker image for prod target
FROM whirlpool-due-base as whirlpool-due-prod

COPY scripts/wait-for-it-prod.sh scripts/wait-for-it-prod.sh
ENTRYPOINT ["bash ./scripts/wait-for-it-prod.sh"]
