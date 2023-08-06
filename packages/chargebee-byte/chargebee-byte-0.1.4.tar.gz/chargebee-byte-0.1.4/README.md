# chargebee-byte

[![Build Status](https://travis-ci.org/ByteInternet/chargebee-byte.svg?branch=master)](https://travis-ci.org/ByteInternet/chargebee-byte)
[![Latest version on PyPI](https://img.shields.io/pypi/v/chargebee-byte.svg?maxAge=2592000)](https://pypi.org/project/chargebee-byte)
[![Licence](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A Python Chargebee API client library. Written by [Byte.nl](https://www.byte.nl).

## Installation

    pip install chargebee_byte

## Usage

```python
import chargebee_byte.client
client = chargebee_byte.client.Client(site_name, api_key)
subscriptions = client.get_all_subscriptions()
```
