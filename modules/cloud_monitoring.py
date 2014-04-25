"""
cloud_monitoring.py - A Rackspace Cloud Monitoring module

Usage:
In the willie config, you will need to add a cloud_monitoring section

[cloud_monitoring]
username = <Rackspace username>
api_key = <API key>
channel = <Channel to which announcements should go>


Copyright 2014, Daniel Givens - daniel@givens.io

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests
import time
import willie
from datetime import datetime, timedelta


@willie.module.commands('alarms')
def alarms(bot, trigger):
    '''Output a list of active Cloud Monitoring alarms'''
    alarms = get_alarms(bot)

    bot.say('Active Cloud Monitoring alarms: {}'.format(len(alarms)))
    for alarm in alarms:
        if alarm['state'] == 'WARNING':
            state = '\x0308WARNING\x03'
        elif alarm['state'] == 'CRITICAL':
            state = '\x0304CRITICAL\x03'
        out = '{} - {} {} {} since {}'.format(alarm['hostname'],
                                              state,
                                              alarm['check'],
                                              alarm['status'],
                                              alarm['timestamp'])
        bot.say(out)


@willie.module.interval(30)
def check_cloud_monitoring(bot):
    if not bot.memory.contains('cloud_monitoring'):
        bot.memory['cloud_monitoring'] = {
            'OK': [],
            'WARNING': [],
            'CRITICAL': []
        }

    alarms = get_alarms(bot)
    get_state_changes(alarms, bot)
    update_alarms(alarms, bot)


def get_alarms(bot):
    response = requests.get(bot.config.cloud_monitoring.dash_url,
                            verify=False)
    alarms = response.json()
    return alarms['alarms']


def update_alarms(alarms, bot):
    states = bot.memory['cloud_monitoring']
    states['OK'] = [alarm['_id']['$oid'] for alarm in alarms
                    if alarm['state'] == 'OK']
    states['WARNING'] = [alarm['_id']['$oid'] for alarm in alarms
                         if alarm['state'] == 'WARNING']
    states['CRITICAL'] = [alarm['_id']['$oid'] for alarm in alarms
                          if alarm['state'] == 'CRITICAL']


def get_state_changes(alarms, bot):
    states = bot.memory['cloud_monitoring']
    if len(states['OK']) == 0:
        first_run = True
    else:
        first_run = False

    for alarm in alarms:
        if alarm['_id']['$oid'] not in states[alarm['state']]:
            if alarm['state'] == 'OK':
                if first_run:
                    continue
                state = '\x0303OK\x03'
            elif alarm['state'] == 'WARNING':
                state = '\x0308WARNING\x03'
            elif alarm['state'] == 'CRITICAL':
                state = '\x0304CRITICAL\x03'
            out = '[Cloud Monitoring] {} {} {} {}'.format(alarm['hostname'],
                                                          alarm['state'],
                                                          alarm['check'],
                                                          alarm['status'])
            if bot.config.cloud_monitoring.channel in bot.channels:
                bot.msg(bot.config.cloud_monitoring.channel, out)
