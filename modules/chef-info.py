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
    env_name = trigger.group(2)
    if env_name is None:
        bot.say('Please give me a chef environment')
        return
    api = chef.autoconfigure()
    envs = chef.Environment.list().names
    if env_name not in envs:
        bot.say("{} isn't an environment I recognize".format(env_name))
        return
    env = chef.Environment(env_name)
    if 'active_set' in env.default_attributes['heat']:
        bot.say('Current active set is {}'.format(
                env.default_attributes['heat']['active_set'].upper()))
    else:
        bot.say('There is no active set for {}'.format(env_name))


@willie.module.commands('environments')
def environments(bot, trigger):
    '''Display a list of chef environments'''
    api = chef.autoconfigure()
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
    api = chef.autoconfigure()
    env = chef.Environment(env_name)
