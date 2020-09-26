# Introduction
This project is the backend for https://ksoccersl.com. It has three parts:
* API for the website
* API for scripts (basic auth)
* Django admin

# Development
## Installation
```
sudo apt install python3.8
sudo apt install python3.8-venv

python3.8 -m venv virtualenv
```
* Visual Studio Code is recommended

## Running the tests
```
. ./virtualenv/bin/activate
cd kbackend
./manage.py test
```

## Running the development server
```
. ./virtualenv/bin/activate
cd kbackend
./manage.py migrate
./manage.py runserver
```

# Production
* Get the .pem file from S3 secrets
* ssh onto the server
```
./connect_to_ec2.sh
```

## Installation
```
sudo su
apt update
apt install docker
apt install docker-compose
```

## (Re-)Deployment
```
git pull
sudo docker-compose build
sudo ./redeploy.sh
```

## Reverting
```
sudo ./revert-deployment.sh
```
> Modify `HEAD~1` in the script if you need to revert multiple commits.
