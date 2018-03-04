#!/bin/sh
APPLICATION_PATH=/home/klimeto/PycharmProjects/dhmz-europa-scrapper/
cd "${APPLICATION_PATH}"
python3 scrapper.py > logs/$(date +%Y-%m-%dT%H-%M-%S).log 2>&1