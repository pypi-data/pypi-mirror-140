# ad-ctf-paas-lib

## Installing

Install and update using pip:

```
pip3 install -U ad-ctf-paas-lib
```


## A Simple Example

Function for ping http service
```
# save as <service_name>.py
import requests
from checker import Checker

check = Checker()

@check.ping
def ping():
    r = requests.get(f"http://{c.address}:80")
    if r.status_code == 200:
        return 'pong'

if __name__ == '__main__':
    c.run()
```