#!/usr/bin/python
# -*- coding: utf-8 -*-
# PagerCentreon
# Copyright 2019 Mathias Da Silva
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "0.1.0"
import sqlite3
import requests
import json
import os
import logging
import time
from datetime import datetime
import unicodedata


#Date
ack_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#Update to match your API key
API_KEY = 'PUT_HERE_YOUR_API_KEY'

# Update to match your chosen parameters
SINCE = ''
UNTIL = ''
DATE_RANGE = ''
STATUSES = ['acknowledged']
INCIDENT_KEY = ''
SERVICE_IDS = ['PUT_HERE_YOUR_SERVICE_ID']
TEAM_IDS = ['']
USER_IDS = []
URGENCIES = []
TIME_ZONE = 'UTC'
SORT_BY = []
INCLUDE = []
inc = []
CONTENT = "."

# Update to match your chosen parameters for the incident
TYPE = 'incident'
SUMMARY = '.'
STATUS = 'acknowledged'
ESCALATION_LEVEL = 1
ASSIGNED_TO_USER = ''
ESCALATION_POLICY = ''

#Logging
LOG_PATH="/var/log/pd_centreon_ack.log"
logging.basicConfig(filename=LOG_PATH,level=logging.INFO)

# Create the database if it doesn't exist.
if not os.path.exists("pd_memory.sqlite"):
        print("No database found, creating new one...")
        logging.info('%s : No database found, creating new one...', ack_date)
        con=sqlite3.connect("pd_memory.sqlite")
        con.execute("create table rememberedPdID(pd_id varchar);")
else:
        con=sqlite3.connect("pd_memory.sqlite")
#Function to check if alerte already ack in database
def isAlertAlreadyAck(pd_id):
 cur=con.cursor()
 cur.execute("select count(*) from rememberedPdID where pd_id=?",(pd_id,))
 r=[row[0] for row in cur.fetchall()][0]
 cur.close()
 return r>0

#Function to store acknowledged id in database
def rememberPdId(pd_id):
 con.execute("insert into rememberedPdID values(?)",(pd_id,))
 con.commit()

#Function to list incidents
def list_incidents():

    url = 'https://api.pagerduty.com/incidents'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY)
    }
    payload = {
        'since': SINCE,
        'until': UNTIL,
        'date_range': DATE_RANGE,
        'statuses[]': STATUSES,
        'incident_key': INCIDENT_KEY,
        'service_ids[]': SERVICE_IDS,
        'team_ids[]': TEAM_IDS,
        'user_ids[]': USER_IDS,
        'urgencies[]': URGENCIES,
        'time_zone': TIME_ZONE,
        'sort_by[]': SORT_BY,
        'include[]': INCLUDE
    }
    r = requests.get(url, headers=headers, params=payload)
    out = r.json()
    return out

#Launch ack if source is service
def ack_svc(host_name,service,acknowledger):
        ack_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ack_timestamp = int(time.time())
        centreon_ack_cmd = 'echo "['+str(ack_timestamp)+'] ACKNOWLEDGE_SVC_PROBLEM;'+host_name+';'+service+';0;0;0;'+acknowledger+';Ack via PagerDuty\" > /var/lib/centreon-engine/rw/centengine.cmd'
        print centreon_ack_cmd
        os.system(centreon_ack_cmd)

#Launch ack if source is host
def ack_host(host_name,acknowledger):
        ack_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ack_timestamp = int(time.time())
        centreon_ack_cmd = 'echo "['+str(ack_timestamp)+'] ACKNOWLEDGE_SVC_PROBLEM;'+host_name+';0;0;0;'+acknowledger+';Ack via PagerDuty\" > /var/lib/centreon-engine/rw/centengine.cmd'
        print centreon_ack_cmd
        os.system(centreon_ack_cmd)
        
#Function to delete accents and weird characters
def strip_accents(unicode_string):
    ndf_string = unicodedata.normalize('NFD', unicode_string)
    is_not_accent = lambda char: unicodedata.category(char) != 'Mn'
    return ''.join(
        char for char in ndf_string if is_not_accent(char)
    )

if __name__ == '__main__':
        out_incidents = list_incidents()
        for i in out_incidents['incidents']:
                incidents = i['incident_key']
                incident_number =  i['incident_number']
                acknowledger = i['acknowledgements'][0]['acknowledger']['summary']
                acknowledger = strip_accents(acknowledger)
                incidents_dict = incidents.split(';')
                event_source = incidents_dict[0].split('=')[-1]
                host_name = incidents_dict[1].split('=')[-1]
                service = incidents_dict[2].split('=')[-1]
                if event_source is 'host':
                         if(isAlertAlreadyAck(incident_number)):
                                continue
                         else:
                                ack_host(host_name,acknowledger)
                                logging.info('%s : %s acknowledge %s ', ack_date, acknowledger, host_name)
                                rememberPdId(incident_number)
                else:
                        if(isAlertAlreadyAck(incident_number)):
                                continue
                        else:
                                ack_svc(host_name,service,acknowledger)
                                logging.info('%s : %s acknowledge %s %s', ack_date, acknowledger, host_name, service)
                                rememberPdId(incident_number)
