#!/bin/bash
while ! ((nc -z whirlpool-rmq 5672) &&
             (nc -z $MEMCACHE_ENDPOINT $MEMCACHE_PORT) &&
             (nc -z $RDS_ENDPOINT $RDS_PORT)); do sleep 3; done
echo "due python evironment is set to: " $PY_ENV
python3 -u ./due/main.py
