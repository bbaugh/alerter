#!/usr/bin/env python
################################################################################
#  twitter_alerts.py
#  Module for sending twitter alerts
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
################################################################################
# Load needed modules
################################################################################
from tweepy import OAuthHandler, API
from base_alerts import base_alerts

################################################################################
# Basic functionality
################################################################################
class twitter_alerts(base_alerts):
  def __init__(self,cfg):
    base_alerts.__init__(self,"twitter")
    self.auth = OAuthHandler(cfg['twitter_consumer_key'], \
                                    cfg['twitter_consumer_secret'])
    self.auth.set_access_token(cfg['twitter_user_key'],\
                               cfg['twitter_user_secret'])
    self.api = API(self.auth)
    self.status = 0



  def alert(self,subject,text):
    if self.status != 0:
      return -1
    if len(text) > 140:
      return -2
    msg = unicode(text)
    stt = self.api.update_status(status=msg)
    if stt == None:
      return 1
    return 0

