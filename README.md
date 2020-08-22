# BL-Shift

![Python >=3.6](https://img.shields.io/badge/python->=3.6-blue.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub last commit](https://img.shields.io/github/last-commit/derekn/blshift/master.svg)](https://github.com/derekn/blshift/commits/master)

[Shift](https://shift.gearboxsoftware.com/) code automated redeemer for [Borderlands](https://borderlands.com/) using lists from [Orcicorn](https://shift.orcicorn.com/).

### Features

-	works for all Borderlands (3, 2, the Pre-Sequel, GOTY), and all platforms (Xbox, PSN, Steam, Nintendo, Stadia, and Epic).
-	automatically pulls active codes from [shift.orcicorn.com](https://shift.orcicorn.com/).
-	codes can also be manually redeemed.
-	supports multiple shift accounts on different platforms.
-	cross-platform written in python.
-	runs on command line so can be easily scripted or put in a [cron](https://www.man7.org/linux/man-pages/man5/crontab.5.html) job to run on a schedule.
-	open-source so you can be assured your logins are safe and secure.
-	provides a reusable package to use in your own python scripts.

### Install

`pip install git+https://github.com/derekn/blshift.git`

or using [pipenv](https://github.com/pypa/pipenv):  
`pipenv install git+https://github.com/derekn/blshift.git#egg=blshift`

### Usage

Specify the Shift account username/password and platform (Xbox/PS/etc.) via the command line options,  
or using the environment variables: `SHIFT_USERNAME`, `SHIFT_PASSWORD` and `SHIFT_PLATFORM`.

```bash
Usage: blshift [OPTIONS]

Options:
  --version                       Show the version and exit.
  -u, --user TEXT                 shift username.  [required]
  -p, --pass TEXT                 shift password.  [required]
  -l, --platform [EPIC|NINTENDO|PLAYSTATION|STADIA|STEAM|XBOX]
                                  redemption platform.  [required]
  -c, --code TEXT                 redeem single shift code, can be used
                                  multiple times.

  --no-cache                      disable shift code caching.
  --help                          Show this message and exit.
```

* Redeem all active codes:  
`blshift -u username -p password -l xbox`

* Manually redeem codes:  
`blshift -u username -p password -l xbox -c CBCTJ-3TJ3J-C3XBS-9RW3C-TTXX2`  
_the `-c/--code` option can be used multiple times to redeem several codes_

* Using environment variables to redeem on multiple platforms  
```bash
export SHIFT_USERNAME='user@email.com'
export SHIFT_PASSWORD='abc123'

blshift --platform xbox
blshift --platform playstation
```
