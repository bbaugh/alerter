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
from json import dumps as jdumps
from requests import post, codes
from base_alerts import base_alerts

################################################################################
# Basic functionality
################################################################################
class slack_alerts(base_alerts):
  def __init__(self,cfg):
    base_alerts.__init__(self,"slack")
    self.urlfrmt = "https://%s/services/hooks/incoming-webhook?token=%s"
    self.domain = cfg['slack_domain']
    self.token = cfg['slack_token']
    self.channel = cfg['slack_channel']
    self.username = cfg['slack_user']
    self.url = self.urlfrmt%(self.domain,self.token)
    self.icon_url = None
    if cfg.has_key('slack_icon_url'):
      self.icon_url = cfg['slack_icon_url']
    self.icon_emoji = None
    if cfg.has_key('slack_icon_emoji'):
      self.icon_emoji = cfg['slack_icon_emoji']
    self.timeout = 2
    if cfg.has_key('slack_timeout'):
      self.timeout = cfg['slack_timeout']
    self.status = 0

  def alert(self,subject,text):
    if self.status != 0:
      return -1
    payload = {'channel': self.channel, 'username': self.username, \
               'text': text}
    if self.icon_url != None:
      payload['icon_url'] = self.icon_url
    if self.icon_emoji != None:
      payload['icon_emoji'] = self.icon_emoji
    r = post(self.url, data=jdumps(payload), timeout=self.timeout)
    if r.status_code == codes.ok:
      return 0
    return r.status_code