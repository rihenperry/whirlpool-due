#!/bin/bash
while ! nc -z whirlpool-rmq 5672; do sleep 3; done
python3 -u ./due/main.py
