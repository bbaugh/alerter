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
try:
  import tweepy
  import base_alerts
except:
  raise Exception( 'Failed to load modules needed for twitter_alerts')


################################################################################
# Basic functionality
################################################################################
class twitter_alerts(base_alerts):
  def __init__(self,cfg):
    self.type = 'twitter'
    try:
      self.auth = tweepy.OAuthHandler(cfg['twitter_consumer_key'], \
                                      cfg['twitter_consumer_secret'])
      self.auth.set_access_token(cfg['twitter_user_key'],\
                                 cfg['twitter_user_secret'])
      self.api = tweepy.API(self.auth)
      self.status = 0
    except:
      self.status = -1


  def alert(subject,text):
    if self.status != 0:
      return -1
    if len(text) > 140:
      return -2
    msg = unicode(text)
    stt = self.api.update_status(status=msg)
    if stt == None:
      return 1
    return 0

