#!/bin/sh
read -p 'Are you sure you want to revert? y/n ' confirmed

if [ "${confirmed}" = "y" ]; then
  echo "Deploying"
  git reset --hard HEAD~1
  sudo docker-compose build
  ./redeploy.sh
  echo "Done"
else
  echo "Aborting..."
fi
