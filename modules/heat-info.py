"""
heat-info.py - Retrieve information from the heat service

Configs:
[heat]
auth_url = https://identity.api.rackspacecloud.com/v2.0
username = <username>
password = <password>
tenant_id = <tenant_id>


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

import json
import willie
import time
from keystoneclient.v2_0.client import Client as keystone_client
from heatclient.client import Client as heat_client


ENDPOINTS = {
    'dfw': 'dfw.orchestration.api.rackspacecloud.com',
    'ord': 'ord.orchestration.api.rackspacecloud.com',
    'iad': 'iad.orchestration.api.rackspacecloud.com',
    'lon': 'lon.orchestration.api.rackspacecloud.com',
    'syd': 'syd.orchestration.api.rackspacecloud.com',
    'hkg': 'hkg.orchestration.api.rackspacecloud.com',
    'staging': 'api.staging.rs-heat.com',
    'inactive.dfw': 'inactive.dfw.orchestration.api.rackspacecloud.com',
    'inactive.ord': 'inactive.ord.orchestration.api.rackspacecloud.com',
    'inactive.iad': 'inactive.iad.orchestration.api.rackspacecloud.com',
    'inactive.lon': 'inactive.lon.orchestration.api.rackspacecloud.com',
    'inactive.syd': 'inactive.syd.orchestration.api.rackspacecloud.com',
    'inactive.hkg': 'inactive.hkg.orchestration.api.rackspacecloud.com',
    'inactive.staging': 'inactive.api.staging.rs-heat.com',
    'qa': 'api.qa.rs-heat.com',
    'dev': 'api.dev.rs-heat.com',
    'fusion.dev': 'fusion.dev.rs-heat.com'
}


class HeatCheck(object):
    def __init__(self, username, password, tenant, auth_url, heat_url,
                 region=None):
        self.username = username
        self.password = password
        self.tenant = tenant
        self.auth_url = auth_url
        self.heat_url = heat_url
        self.region = region
        self.stack_list = []

        keystone = keystone_client(username=self.username,
                                   password=self.password,
                                   tenant_name=self.tenant,
                                   auth_url=self.auth_url)
        self.token = keystone.auth_token
        self.heat = heat_client('1', endpoint=self.heat_url,
                                region_name=self.region, token=self.token,
                                insecure=True)

    def build_info_time(self):
        try:
            start = time.time()
            build_info = self.heat.build_info.build_info()
            return time.time() - start
        except BaseException, e:
            print(e)
            return None

    def stack_list_time(self):
        try:
            start = time.time()
            self.stack_list = list(self.heat.stacks.list())
            return time.time() - start
        except BaseException, e:
            print(e)
            return None

    def stack_show_time(self):
        try:
            if len(self.stack_list) > 0:
                start = time.time()
                stack_show = self.heat.stacks.get(self.stack_list[0].id)
                return time.time() - start
            return None
        except BaseException, e:
            print(e)
            return None

    def stack_preview_time(self, template_url, parameters=None):
        if parameters:
            kwargs = {'stack_name': 'test', 'template_url': template_url,
                      'parameters': parameters}
        else:
            kwargs = {'stack_name': 'test', 'template_url': template_url}

        try:
            start = time.time()
            stack = self.heat.stacks.preview(**kwargs)
            return time.time() - start
        except BaseException, e:
            print(e)
            return None


@willie.module.commands('build-info')
@willie.module.example('.build-info staging', 'api: 2014.i3-20140414-666  '
                       'engine: 2014.i3-20140414-666  fusion: '
                       'i3-20140411-11938a1-6')
def build_info(bot, trigger):
    '''Display build-info for a heat endpoint'''
    username = bot.config.heat.username
    password = bot.config.heat.password
    tenant_name = bot.config.heat.tenant_name
    auth_url = bot.config.heat.auth_url
    endpoint_input = trigger.group(2)
    endpoints_list = []
    regions = ['dfw', 'iad', 'ord', 'lon', 'syd', 'hkg']

    if endpoint_input is None:
        bot.say("Please give me an endpoint to get build-info from. See "
                ".heat-endpoints for a list.")
        return
    elif endpoint_input == 'all':
        endpoints_list = [endpoint for endpoint in ENDPOINTS]
    elif endpoint_input == 'active':
        endpoints_list = regions
    elif endpoint_input == 'inactive'
        endpoints_list = ['inactive.'+ endpoint for region in regions]
    if endpoint_input not in ENDPOINTS:
        bot.say("{} isn't an endpoint name I recognize. See a list at "
                ".heat-endpoints".format(endpoint_input))
        return

    keystone = keystone_client(username=username, password=password,
                               tenant_name=tenant_name, auth_url=auth_url)
    token = keystone.auth_token

    for endpoint_label in endpoints_list:
        full_endpoint = 'https://{}/v1/{}'.format(ENDPOINTS[endpoint_label],
                                                  bot.config.heat.tenant_name)
        heat = heat_client('1', endpoint=full_endpoint, insecure=True, token=token)

        build_info = heat.build_info.build_info()
        api_revision = build_info['api']['revision']
        engine_revision = build_info['engine']['revision']
        if 'fusion-api' in build_info:
            fusion_revision = build_info['fusion-api']['revision']
        else:
            fusion_revision = 'None'

        bot.say('{}: api: {}  engine: {}  fusion: {}'.format(
                endpoint_label,
                api_revision,
                engine_revision,
                fusion_revision))

@willie.module.commands('heat-endpoints')
def heat_endpoints(bot, trigger):
    '''Display all of the heat endpoints I'm aware of'''
    if not trigger.is_privmsg:
        bot.reply("I am sending you a private message with all of the "
                  "endpoints and their short names.")
    bot.msg(trigger.nick, "Here are the endpoint short names and fqdn's:")
    width = max([len(key) for key in ENDPOINTS])
    for key, value in ENDPOINTS.iteritems():
        bot.msg(trigger.nick, '{name:{width}s} {fqdn}'.format(name=key,
                fqdn=value, width=width))


@willie.module.commands('health')
def health(bot, trigger):
    '''Do some health checks on an endpoint'''
    username = bot.config.heat.username
    password = bot.config.heat.password
    tenant_name = bot.config.heat.tenant_name
    auth_url = bot.config.heat.auth_url
    endpoint_label = trigger.group(2)

    if endpoint_label is None:
        bot.say("Please give me an endpoint to get build-info from. See "
                ".heat-endpoints for a list.")
        return

    if endpoint_label not in ENDPOINTS:
        bot.say("{} isn't an endpoint name I recognize. See a list at "
                ".heat-endpoints".format(endpoint_label))
        return

    heat_url = 'https://{}/v1/{}'.format(ENDPOINTS[endpoint_label],
                                         bot.config.heat.tenant_name)

    heat_check = HeatCheck(username, password, tenant_name, auth_url, heat_url)
    bi_time = heat_check.build_info_time()
    sl_time = heat_check.stack_list_time()
    ss_time = heat_check.stack_show_time()
    bot.say('build-info: {:.2}s  stack-list: {:.2}s  stack-show: {:.2}s'.format(bi_time,
            sl_time, ss_time))
