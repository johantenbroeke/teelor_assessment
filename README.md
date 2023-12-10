# Perfect Parcel

## Setup local env

clone this repo:

    git clone git@github.com:teelor-rotterdam/johan_ten_broeke.git

Setup Virtual env (recommended)

    virtualenv venv --python=python3.10

Activate venv:

    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

## run the test suite

    pytest

## run the dev server

    python manage.py runserver 0.0.0.0:7777

## Demo users

In the sqlite db there is an admin user.

    username: admin
    password: admin

This user can upload container-xml, create organisations, create departments and configure business rules for organisations.
This user can also create and assign users to organisations.

There is also an demo user.

    username: demo
    password: parcel123

This user can not access the Django admin and only upload XML and process parcels for his organisation.

*NOTE: Each container-id can only be uploaded once.*
