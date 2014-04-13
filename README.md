# Rackspace Cloud Orchestration IRC Bot Modules

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
```

#### Commands

`.alerts` - Responds with a count and list of current active alerts
