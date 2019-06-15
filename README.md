# PagerCentreon
[![License](https://img.shields.io/pypi/l/supervisor-alert.svg)](https://github.com/Drbmk/supervisor-pushbullet/blob/master/LICENSE)

## Usage:

PagerCentreon is intended to be run on set intervals to check the PagerDuty API
for active incidents that have been acknowledged in PagerDuty but not in Centreon -
PagerCentreon handles the host / service acknowledgement back to Centreon.

Acknowledged services and hosts are stored in a SQLite3 database for persistence 

Relies on Centreon cmd to interact with Centreon

## Parameters 

You have to set your API_KEY to interact with PagerDuty API.
You also can filter the paylod with this parameters :

SINCE = ''

UNTIL = ''

DATE_RANGE = ''

STATUSES = ['acknowledged']

INCIDENT_KEY = ''

SERVICE_IDS = ['XXXX']

TEAM_IDS = ['']

USER_IDS = []

URGENCIES = []

TIME_ZONE = 'UTC'

SORT_BY = []

INCLUDE = []

inc = []


CONTENT = "."

## Example:

*/1 * * * * centreon /opt/scripts/PagerCentreon.py

