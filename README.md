# BL-Shift

![Python >=3.7](https://img.shields.io/badge/python->=3.7-blue.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub last commit](https://img.shields.io/github/last-commit/derekn/blshift/master.svg)](https://github.com/derekn/blshift/commits/master)

[Shift](https://shift.gearboxsoftware.com/) code automated redeemer for [Borderlands](https://borderlands.com/) using lists from [Orcicorn](https://shift.orcicorn.com/).

### Install

`pip install git+ssh://git@github.com/derekn/blshift.git`

### Usage

Specify the Shift account username/password via the command line options,  
or using the environment variables: `SHIFT_USERNAME` and `SHIFT_PASSWORD`.

```bash
Usage: blshift [OPTIONS]

Options:
  -u, --user TEXT  shift username  [required]
  -p, --pass TEXT  shift password  [required]
  -c, --code TEXT  redeem single shift code, can be used multiple times
  --help           Show this message and exit.
```

* Redeem all active codes:  
`blshift -u username -p password`

* Manually redeem codes:  
`blshift -u username -p password -c CBCTJ-3TJ3J-C3XBS-9RW3C-TTXX2`  
_the `-c/--code` option can be used multiple times to redeem several codes_
