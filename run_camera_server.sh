#!/bin/bash
export FLASK_APP=security_camera_api.py
sudo -E flask run --host=0.0.0.0 --port=80
