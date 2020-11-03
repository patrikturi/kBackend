## Set up service

Copy the config file to `/etc/systemd/system/kbackend.service`
Then:
```
sudo systemctl enable kbackend
sudo systemctl start kbackend
```

Reload config:
```
sudo systemctl daemon-reload
```

Logs:
```
sudo journalctl -u kbackend
```
