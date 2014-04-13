# Rackspace Cloud Orchestration IRC Bot

A collection of [Willie](http://willie.dftba.net/) modules used for the Cloud
Orchestration IRC bot.

## Usage

Put the modules in `~/.willie/modules` and update `~/.willie/default.cfg` where
appropriate.

## Modules

### cloud_monitoring.py

Polls Rackspace Cloud Monitoring for active alerts on a 30 second interval

#### Configs

```
[cloud_monitoring]
username = <Rackspace Cloud username>
api_key = <Rackspace Cloud api key>
channel = <Channel where notifications are sent>
```

#### Commands

`.alerts` - Responds with a count and list of current active alerts

## Copyright & License

Copyright 2014, Daniel Givens <daniel@givens.io>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
