# [Nomics REST API](https://nomics.com/) wrapper

[![py-nomics-client-pypi](https://img.shields.io/pypi/v/py-nomics-client.svg)](https://pypi.python.org/pypi/py-nomics-client)

Nomics REST API Doc: https://nomics.com/docs/

## Install

```bash
pip install py-nomics-client
```

## Usage

```python
from nomics import Nomics

n = Nomics(key="<your-key-here>")
n.get_market(base="BTC", quote="USD")
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
