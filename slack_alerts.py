#!/usr/bin/env python
################################################################################
#  slack_alerts.py
#  Module for sending slack alerts
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
################################################################################
# Load needed modules
################################################################################
try:
  import json
  import requests
except:
  raise Exception( 'Failed to load modules needed for slack_alerts')

################################################################################
# Basic functionality
################################################################################
class twitter_alerts(cfg):
  def __init__(self):
    self.urlfrmt = "https://%s/services/hooks/incoming-webhook?token=%s"
    try:
      self.domain = cfg['slack_domain']
      self.token = cfg['slack_token']
      self.channel = cfg['slack_channel']
      self.username = cfg['slack_user']
      self.url = self.urlfrmt%(self.domain,self.webhook_token)
      self.icon_url = cfg['slack_icon_url']
      self.timeout = cfg['slack_timeout']
      self.status = 0
    except:
      self.status = -1
  def alert(subject,text):
    if self.status != 0:
      return -1
    payload = {'channel': self.channel, 'username': self.username, \
               'text': text, 'icon_url': self.icon_url}
    r = requests.post(url, data=json.dumps(payload), timeout=self.timeout)
    return r.status_code