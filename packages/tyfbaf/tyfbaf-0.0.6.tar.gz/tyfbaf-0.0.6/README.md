# tyfbaf

![Version](https://img.shields.io/pypi/v/tyfbaf)
![License](https://img.shields.io/pypi/l/tyfbaf)
![Downloads](https://img.shields.io/pypi/dd/tyfbaf)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**tyfbaf** is a Python package designed for bringing (even) more joy when using the _[SAP® BusinessObjects™ RESTful Web Service SDK](https://help.sap.com/viewer/58f583a7643e48cf944cf554eb961f5b/4.2/en-US)_.

## Install

You can install via PIP: `pip install tyfbaf`

## Basic Usage

First you have to call the setup function to tell **tyfbaf** the name of your server (and optionally your port, if it's differing from 6405):

```python
>>> import tyfbaf
>>> tyfbaf.setup("my-server-name", port=1234)
```

Then **tyfbaf** gives you a get and a post function in the http module. Those functions are specialized for the _SAP® BusinessObjects™ RESTful Web Service SDK_. So you just have to call the desired endpoint, you can pass your token as a parameter, you don't have to set up headers, etc.

```python
>>> import tyfbaf.http
>>> tyfbaf.http.get("/logon/long")
{'password': '', 'clientType': '', 'auth': 'secEnterprise', 'userName': ''}
```

For common cases, **tyfbaf** gives you predefined functions, too. So for example you can request a token like this.

```python
>>> import tyfbaf.token
>>> tyfbaf.token.request("my-username", "my-password123")
my-server-name:6400@{3&2=5595,U3&p=40674.9596541551,Y7&4F=12,U3&63=secEnterprise,0P&66=60,03&68=secEnterprise:my-username,0P&qe=100,U3&vz=SFY6agrLPxpfQBK1ZKYCahEZKCbfsQm7VgWZFiH.RhM,UP
```

## Contributions

_tyfbaf_ neither claims to be complete nor perfect. If you bump into any kind of bug, please let us know by [opening an issue](https://github.com/yveso/tyfbaf/issues/new). If you have an idea for a new feature, please also [open an issue](https://github.com/yveso/tyfbaf/issues/new). So we could work things out and make the world a little, little, tiny bit better. 😎

## Changelog

See [CHANGELOG.md](https://github.com/yveso/tyfbaf/blob/main/CHANGELOG.md) for more information.

## License

Distributed under the MIT License. See [LICENSE](https://github.com/yveso/tyfbaf/blob/main/LICENSE) for more information.

## Copyright

_SAP® BusinessObjects™_ is the trademark or registered trademark of SAP SE or its affiliates in Germany and in several other countries.

**tyfbaf** is not affiliated, associated, authorized, endorsed by or in any way officially connected to SAP SE or an SAP affiliate company.
