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

except:
  print 'Failed to load modules'
  _exit(-1)


def email(smtpsrv,sender,recipient,subject,text):
  msg = MIMEText.MIMEText(text)
  # sender == the sender's email address
  # recipient == the recipient's email address
  msg['Subject'] = subject
  msg['From'] = sender
  if hasattr(recipient,'__iter__'):
    msg['To'] = ','.join(recipient)
  else:
    msg['To'] = recipient
  
  # Send the message via our own SMTP server, but don't include the
  # envelope header.
  s = smtplib.SMTP(smtpsrv)
  s.sendmail(sender, msg['To'].split(','), msg.as_string())
  s.quit()
