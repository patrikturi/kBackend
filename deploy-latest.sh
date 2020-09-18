#!/bin/sh
git pull
sudo docker-compose build
./redeploy.sh
