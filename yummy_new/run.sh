#!/usr/bin/env bash

export FLASK_APP=app.py
export FLASK_ENV=development

flask init-db
flask run