# Local

## Pre-Setup
Ideally use pyenv with Python 3.8+ do run the steps ahead. You can use SQLite locally, but to emulate prod
setup preferably use PostgreSQL. You can override default settings such as db settings in `taggedweb/override_settings.py`.


OS X
```zsh
brew install postgresql
```

## Setup

Pre-reqs, setup pyenv with pyenv virtualenv before on your environment

```bash

# This will create a virtualenv called tweb with Python 3.9.4
pyenv virtualenv 3.9.4 tweb

# This will activate your tweb environment for this project
source activate tweb

# For psycopg2 dependencies some C libraries may need to be on path,
# if this fails then google the error you see
pip install -r requirements.txt

# Each time there is a change in models/migrations you have to fetch
# the code and run this
python manage.py migrate

# To start the server locally at the default port 8000
python manage.py runserver
```

For changing any local only settings (for your computer), don't directly edit settings.py, update over

## Optional Setup

    python manage.py cities_light

This will take a bit of time to load all the cities data.

## Tests

The project is configured to use the pytest test runner, just run the following to run all tests to,
verify your local installation is running correctly.

    pytest

# Prod

## Pre-Setup

For the database we use an RDS PostgreSQL instance.

Add the following libraries to install Geographic utilities.

    sudo apt-get install binutils libproj-dev gdal-bin

## Setup

Same steps as local + also requires some additional prod setup, like nginx configuration and starting the WSGI application
via gunicorn instead of using the dev server.

To update the nginx config after updating nginx_config.txt in this repository, run the following:

```bash
# Sudo becauses the nginx dest config needs extra write permissions
sudo cp taggedweb/nginx_conf.txt /etc/nginx/sites-available/taggedweb.com
sudo ln -s /etc/nginx/sites-available/taggedweb.com /etc/nginx/sites-enabled/taggedweb.com

# Relaod nginix if it's already running for settings to apply or start it
sudo nginx -s reload
```

For the time being gunicorn is being run on a unix `screen` called `taggedweb`. Later on this should be moved to being managed by supervisord.

```bash
# screen -r wsgi to resume or screen -S wsgi to start a new screen
cd taggedweb # directory with manage.py
# Run the following to start gunicorn WSGI service on default port 8000
# (Ideally run in background or in dev/early stages just spin off on a screen)
gunicorn taggedweb.wsgi -b 127.0.0.1:8001
```


## HTTPS/SSL Certificate

LetsEncrypt SSL cert setup. The cert is already setup by following instructions [here](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04).
Command to run on the server (Don't need to run now as it is set to auto-renew with certbot.timer). The instructions are
only added here in case the deploy is to be performed on a new instance.

```bash
sudo certbot --nginx -d taggedweb.com -d api.taggedweb.com -d www.taggedweb.com
```
