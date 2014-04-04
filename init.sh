#!/bin/bash

virtualenv .

echo "export PYTHONPATH=$(pwd)" >> bin/activate

echo "Complete"
