#!/usr/bin/env bash

cd /opt/pihole-metrics

rm -rf venv

python3 -m venv venv

source venv/bin/activate

pip3 -r requirements.txt

deactivate

exit 0