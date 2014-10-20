#!/usr/bin/env python
################################################################################
#  email_alerts.py
#  Module for sending email alerts
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
################################################################################
# Load needed modules
################################################################################
try:
  from email import MIMEText
  import smtplib
  import base_alerts
except:
  raise Exception( 'Failed to load modules needed for email_alerts')

################################################################################
# Basic functionality
################################################################################
class email_alerts(base_alerts):
  def __init__(self,cfg):
    self.type = 'email'
    try:
      self.sender = cfg['email_sender']
      self.recipient = cfg['email_recipient']
      self.smtp = cfg['email_smtp']
      self.status = 0
    except:
      self.status = -1

  def alert(subject,text):
    if self.status != 0:
      return -1
    msg = MIMEText.MIMEText(text)
    # sender == the sender's email address
    # recipient == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = self.sender
    if hasattr(self.recipient,'__iter__'):
      msg['To'] = ','.join(self.recipient)
    else:
      msg['To'] = self.recipient
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    try:
      s = smtplib.SMTP(smtpsrv)
      s.sendmail(sender, msg['To'].split(','), msg.as_string())
      s.quit()
      return 0
    except:
      return 1
