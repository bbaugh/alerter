#!/usr/bin/env python
################################################################################
#  base_alerts.py
#  
#
#  Created by Brian Baughman on 10/20/14.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################


################################################################################
# Basic functionality
################################################################################
class base_alerts:
  def __init__(self,name):
    self.type = name
    self.status = -2

  def alert(subject,text):
    return -1
