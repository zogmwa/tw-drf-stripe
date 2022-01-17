# Local

## Pre-Setup
Ideally use pyenv with Python 3.8+ do run the steps ahead. You can use SQLite locally, but to emulate prod
setup preferably use PostgreSQL. You can override default settings such as db settings in `taggedweb/override_settings.py`.


OS X: You can preferably install app from [here](https://postgresapp.com/) or use homebrew to install it:

```zsh
brew install postgresql
```

## Setup

Pre-reqs, setup pyenv with pyenv virtualenv before on your environment

```zsh

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

For changing any local only settings (for your computer), don't directly edit settings.py, copy over override_settings.py.dist,
to override_settings.py and update that.

```bash
cp override_settings.py.dist override_settings.py
```

Now, you can add any custom settings you want to use specifically for local only (without affecting prod) to override_settings.

### ElasticSearch

We use ElasticSearch for our search indexes. Download and install from here:
https://www.elastic.co/downloads/elasticsearch
Tested during v7.12.1

After installing it, simply run the following to start elasticsearch:

    elasticsearch

## Tests

The project is configured to use the pytest test runner, just run the following to run all tests to,
verify your local installation is running correctly.

    pytest

## Populating test data in your local db

```bash
    # This will sync Product and Price data from stripe test to local db creating djstripe.models.Product/Price instances.
    python manage.py djstripe_sync_models Product Price
    
    # This will create api.models.Solution instances (Solutions is the term we use for what we are selling)
    python create_solutions_from_products
```

# Production Only (Skip for Local)

The below setup is for production only, skip this for local.

## Pre-Setup

For the database we use an RDS PostgreSQL instance.

### ElasticSearch

First setup an ElasticSearch cluster. This is onetime. We are currently using Elastic.co for our elasticsearch cluster.
(`pranjal@taggedweb.com` is the primary account holder, ping him for details if you want to connect to it from local to
play around. Though normally for local you'd use a local instance of Elasticsearch).

To initialize/rebuild search indexes for existing models:

```bash
python manage.py search_index --rebuild
```

Note this will prompt if it can delete and recreate index, you can say yes. That is because we aren't using ElasticSearch
as primary storage of mission-critical data, just indexes that are built on top of the  underlying SQL database.

## Setup

Same steps as local + also requires some additional prod setup, like nginx configuration and starting the WSGI application
via gunicorn instead of using the dev server.

To update the nginx config after updating nginx_config.txt in this repository, run the following:

```bash
# Sudo becauses the nginx dest config needs extra write permissions
sudo cp taggedweb/nginx_conf.txt /etc/nginx/sites-available/api.taggedweb.com
sudo ln -s /etc/nginx/sites-available/taggedweb.com /etc/nginx/sites-enabled/api.taggedweb.com

# Relaod nginix if it's already running for settings to apply or start it
sudo nginx -s reload
```

The guinicorn process is managed via supervisord in prod, supervisord config that we are using is defined here:
[supervisor taggedweb configuration](https://github.com/taggedweb/taggedweb-devops/blob/main/supervisor-config/taggedweb.conf)

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
sudo certbot --nginx -d api.taggedweb.com
```

## Generate Sitemap File

When the code is being set up for the first time on production, run the following command to generate the sitemap files,
including the index sitemap. The sitemap files are pushed to S3. taggedweb-frontend repo has a page for sitemaps at,
www.taggedweb.com/sitemap.xml, which is basically a layer over S3. Frontend pulls the file from the S3 bucket and serves it.

```bash
# Generate all (Solution detail, Software detail, Software list, Index) sitemap files:
python manage.py generate_sitemap_full
```
