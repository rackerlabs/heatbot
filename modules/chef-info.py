"""
rs-heat.py - Rackspace Cloud Orchestration module

Usage:
For pychef usage, there must be a standard chef config in ~/.chef


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
import willie
import chef


@willie.module.commands('active')
def active(bot, trigger):
    '''Display the current active set for an environment'''
    env_input = trigger.group(2)
    if env_input is None:
        bot.say('Please give me a chef environment')
        return
    url = bot.config.chef.url
    key = bot.config.chef.key
    username = bot.config.chef.username
    api = chef.ChefAPI(url, key, username)
    api.set_default()
    all_envs = chef.Environment.list().names
    if env_input in ('prod', 'production', 'all'):
        #Select all production environments
        envs = [env for env in all_envs if 'production-' in env]

        if env_input == 'all':
            envs.append('staging')
    elif env_input in all_envs:
        envs = [env_input]
    elif 'production-' + env_input in all_envs:
        envs = ['production-' + env_input]
    else:
        bot.say("{} isn't an environment I recognize".format(env_input))
        return

    for env_name in sorted(envs):
        env = chef.Environment(env_name)
        if 'active_set' in env.default_attributes['heat']:
            bot.say('{}: Current active set is {}'.format(
                    env_name,
                    env.default_attributes['heat']['active_set'].upper()))
        else:
            bot.say('There is no active set for {}'.format(env_name))

@willie.module.commands('environments')
def environments(bot, trigger):
    '''Display a list of chef environments'''
    url = bot.config.chef.url
    key = bot.config.chef.key
    username = bot.config.chef.username
    api = chef.ChefAPI(url, key, username)
    api.set_default()
    envs = chef.Environment.list().names
    bot.say('Chef environments: {}'.format(', '.join(
            chef.Environment.list().names)))


@willie.module.commands('chef_noop')
def chef_noop(bot, trigger):
    '''Display a list of noop hosts in a chef environment'''
    env_name = trigger.group(2)
    if env_name is None:
        bot.say('Please give me a chef environment')
        return
    url = bot.config.chef.url
    key = bot.config.chef.key
    username = bot.config.chef.username
    api = chef.ChefAPI(url, key, username)
    api.set_default()
    env = chef.Environment(env_name)
    noop = env.default_attributes['base']['noop']
    bot.say('The following nodes have noop set: {}'.format(', '.join(noop)))
