# [Cryptowatch API](https://cryptowat.ch/) wrapper

[![py-cryptowatch-client-pypi](https://img.shields.io/pypi/v/py-cryptowatch-client.svg)](https://pypi.python.org/pypi/py-cryptowatch-client)

Cryptowatch Doc: https://docs.cryptowat.ch/rest-api/

## Install

```bash
pip install py-cryptowatch-client
```

## Usage

```python
from cryptowatch import Cryptowatch

cw = Cryptowatch(key=None)
cw.get_market_prices()
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
