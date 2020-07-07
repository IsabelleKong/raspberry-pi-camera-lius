#!/bin/bash
export FLASK_APP=lius_server.py
sudo -E flask run --host=0.0.0.0 --port=80
