# Rawproxy

a tiny proxy server for raw.githubusercontent.com 


## Deploy to ubuntu server

```commandline
ln -s $(python3 -m site --user-site)/rawproxy/rawproxy.service /etc/systemd/system/rawproxy.service
sudo systemctl daemon-reload
sudo systemctl start rawproxy.service
```

