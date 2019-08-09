FROM python:3.7.4-buster as whirlpool-due-base

ENV PYTHONDONTWRITEBYTECODE=1
ARG WH_DUE_ROOT=/home/whirlpool/whirlpool-due
WORKDIR $WH_DUE_ROOT

RUN apt-get update \
  && apt-get install -y --no-install-recommends netcat \
  && rm -rf /var/lib/apt/lists/* \
  && useradd --create-home --shell /bin/bash whirlpool \
  && chown -R whirlpool:whirlpool $WH_DUE_ROOT

# files necessary to build the project
COPY .pylintrc ./
COPY requirements.txt ./

RUN mkdir logs/ \
  && pip3 install -r requirements.txt

COPY scripts/ scripts/
COPY due/ due/

# docker image for dev target
FROM whirlpool-due-base as whirlpool-due-dev

COPY scripts/wait-for-it.sh scripts/wait-for-it.sh
ENTRYPOINT ["bash ./scripts/wait-for-it.sh"]

# docker image for prod target
FROM whirlpool-due-base as whirlpool-due-prod

COPY scripts/wait-for-it-prod.sh scripts/wait-for-it-prod.sh
ENTRYPOINT ["bash ./scripts/wait-for-it-prod.sh"]
