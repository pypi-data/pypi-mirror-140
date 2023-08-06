# [CoinMarketCap API](https://coinmarketcap.com/) wrapper

[![py-coinmarketcap-client-pypi](https://img.shields.io/pypi/v/py-coinmarketcap-client.svg)](https://pypi.python.org/pypi/py-coinmarketcap-client)

CoinMarketCap API Doc: https://coinmarketcap.com/api/documentation/v1/

## Install

```bash
pip install py-coinmarketcap-client
```

## Usage

```python
from coinmarketcap import CoinMarketCap

cmc = CoinMarketCap(key="<your-key-here>", key_type="Basic")
cmc.get_info(id=1)
```

## Testing

```bash
virtualenv venv
source ./venv/bin/activate
pip install -r dev_requirements.txt
deactivate
source ./venv/bin/activate
pytest
```
