## Change password, create db
```
sudo -u postgres psql
ALTER USER postgres PASSWORD '';
CREATE DATABASE kbackend ENCODING 'utf-8';
```

## Move database
```
sudo mv /var/lib/postgresql/10/main /mnt/data/db
sudo nano /etc/postgresql/10/main/postgresql.conf
data_directory = '/mnt/data/db'
```

## Connect from docker
https://lchsk.com/how-to-connect-to-a-host-postgres-database-from-a-docker-container.html
sudo service postgresql restart

## Load sqlite db
https://stackoverflow.com/a/30544492
sudo -u postgres pgloader command
