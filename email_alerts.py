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
  from email.mime.text import MIMEText
except:
  try:
    from email.mime.Text import MIMEText
  except:
    from email import MIMEText
from smtplib import SMTP
from base_alerts import base_alerts


################################################################################
# Basic functionality
################################################################################
class email_alerts(base_alerts):
  def __init__(self,cfg):
    base_alerts.__init__(self,"email")
    self.sender = cfg['email_sender']
    self.recipient = cfg['email_recipient']
    self.smtp = cfg['email_smtp']
    self.status = 0

  def alert(self,subject,text):
    if self.status != 0:
      return -1
    msg = MIMEText(text)
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
      s = SMTP(smtpsrv)
      s.sendmail(sender, msg['To'].split(','), msg.as_string())
      s.quit()
      return 0
    except:
      return 1
