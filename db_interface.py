#!/usr/bin/env python
################################################################################
#  db_interface
#  Module for interfacing with sqlite DB
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
################################################################################
# Load needed modules
################################################################################
try:
  from sqlite3 import connect
except:
  try:
    from sqlite import connect
  except:
    print 'Unable to load database interface.'
    raise

################################################################################
#  DB configuration class
################################################################################
class dbcfgobj:
  def __init__(self,fname):
    self.fname = fname
    self.dbconn =  connect(fname)
    self.curs  = self.dbconn.cursor()
  def checktbl(self,tblstruct):
    '''
      Creates a table given:
        dbcfg     - sqlite cursor object
        tblstruct - structure of table to be constructed
          tblstruct is a dictionary with the following entries:
            tblname - name of table to be created
            colname - colname can be anything other than tblname and is a
                      dictonary containing:
                        index - interger index
                        type - data type to be stored
                        nullst - null state
    '''
    # Connect to DB
    dbtblck = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
    dbtblck = dbtblck%(tblstruct['tblname'])
    self.curs.execute(dbtblck)
    dbtblstate = self.curs.fetchone()
    rstatus = 0
    if dbtblstate == None:
      rstatus = self.definetbl(tblstruct)
    return rstatus
  def definetbl(self,tblstruct):
    '''
      Creates a table given:
        dbcfg     - sqlite cursor object
        tblstruct - structure of table to be constructed
          tblstruct is a dictionary with the following entries:
            tblname - name of table to be created
            colname - colname can be anything other than tblname and is a
                      dictonary containing:
                        index - interger index
                        type - data type to be stored
                        nullst - null state
    '''
    carr = ["" for i in xrange(len(tblstruct)-1)]
    for k,val in tblstruct.iteritems():
      if k == 'tblname':
        continue
      carr[val['index']] = "%s %s %s"%(k,val['type'],val['nullst'])
    dbctbl = "CREATE TABLE %s ( %s );"%(tblstruct['tblname'],','.join(carr))
    self.curs.execute(dbctbl)
    dbtblck = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
    dbtblck = dbtblck%(tblstruct['tblname'])
    self.curs.execute(dbtblck)
    dbtblstate = self.curs.fetchone()
    if dbtblstate == None:
      return -1
    return 0


