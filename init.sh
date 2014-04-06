#!/bin/bash

virtualenv .

echo "export PYTHONPATH=$(pwd)" >> bin/activate

source bin/activate
pip install -r requirements.txt

echo "Complete. Don't forget to run '. bin/activate'"
