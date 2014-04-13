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

import pyrax
import time
import willie
from datetime import datetime, timedelta


@willie.module.commands('alerts')
def alerts(bot, trigger):
    '''Output a list of active Cloud Monitoring alerts'''
    username = bot.config.cloud_monitoring.username
    api_key = bot.config.cloud_monitoring.api_key
    pyrax.set_setting("identity_type", "rackspace")
    pyrax.set_credentials(username, api_key)
    cm = pyrax.cloud_monitoring

    view = cm.get_overview()
    alerts = get_alerts(view, bot)
    active_alerts = [alert for alert in alerts if alert['state'] != 'OK']
    bot.say('Active Cloud Monitoring alerts: {}'.format(len(active_alerts)))
    for alert in active_alerts:
        last_change = datetime.fromtimestamp(alert['timestamp'] / 1000)
        if alert['state'] == 'WARNING':
            state = '\x0308WARNING\x03'
        elif alert['state'] == 'CRITICAL':
            state = '\x0304CRITICAL\x03'
        out = '{} - {} {} {} since {}'.format(alert['entity_label'],
                                              alert['check_label'],
                                              alert['label'], state,
                                              last_change.strftime('%c'))
        bot.say(out)


@willie.module.interval(30)
def check_cloud_monitoring(bot):
    username = bot.config.cloud_monitoring.username
    api_key = bot.config.cloud_monitoring.api_key
    pyrax.set_setting("identity_type", "rackspace")
    pyrax.set_credentials(username, api_key)

    if not bot.memory.contains('cloud_monitoring'):
        bot.memory['cloud_monitoring'] = {
            'OK': [],
            'WARNING': [],
            'CRITICAL': []
        }

    cm = pyrax.cloud_monitoring
    view = cm.get_overview()
    alerts = get_alerts(view, bot)
    get_state_changes(alerts, bot)
    update_alarms(alerts, bot)


def get_alerts(view, bot):
    alerts = []
    for item in view['values']:
        for alarm_state in item['latest_alarm_states']:
            alarm_label = (alarm['label'] for alarm in item['alarms']
                           if alarm['id'] == alarm_state['alarm_id']).next()
            check_label = (check['label'] for check in item['checks']
                           if check['id'] == alarm_state['check_id']).next()
            alerts.append({
                'id': alarm_state['alarm_id'],
                'label': alarm_label,
                'state': alarm_state['state'],
                'timestamp': alarm_state['timestamp'],
                'check_label': check_label,
                'entity_label': item['entity']['label']
            })

    return alerts


def update_alarms(alerts, bot):
    states = bot.memory['cloud_monitoring']
    states['OK'] = [alarm['id'] for alarm in alerts
                    if alarm['state'] == 'OK']
    states['WARNING'] = [alarm['id'] for alarm in alerts
                         if alarm['state'] == 'WARNING']
    states['CRITICAL'] = [alarm['id'] for alarm in alerts
                          if alarm['state'] == 'CRITICAL']


def get_state_changes(alerts, bot):
    states = bot.memory['cloud_monitoring']
    if len(states['OK']) == 0:
        first_run = True
    else:
        first_run = False

    for alarm in alerts:
        if alarm['id'] not in states[alarm['state']]:
            if alarm['state'] == 'OK':
                if first_run:
                    continue
                state = '\x0303OK\x03'
            elif alarm['state'] == 'WARNING':
                state = '\x0308WARNING\x03'
            elif alarm['state'] == 'CRITICAL':
                state = '\x0304CRITICAL\x03'
            out = 'Cloud Monitoring: {} {} on {} {}'.format(
                  alarm['check_label'],
                  alarm['label'],
                  alarm['entity_label'],
                  state)
            if bot.config.cloud_monitoring.channel in bot.channels:
                bot.msg(bot.config.cloud_monitoring.channel, out)
