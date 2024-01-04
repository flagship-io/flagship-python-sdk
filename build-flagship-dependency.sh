#!/bin/bash
rm -rf ./dependencies
mkdir -p ./dependencies/python
python -m pip install . -t ./dependencies/python