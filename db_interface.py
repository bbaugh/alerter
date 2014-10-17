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
  try:
    from sqlite3 import connect
  except:
    try:
      from sqlite import connect
    except:
      sys.exit(-2)
except:
  print 'Failed to load modules'
  _exit(-1)

################################################################################
#  DB configuration class
################################################################################
class dbcfgobj:
  def __init__(self):
    self.fname = None
    self.dbconn = None
    self.curs  = None


def connectdb(fname):
  '''
    Connects to a sqlite file given:
      fname - name of sqlite file to open

  '''
  odbcfg = dbcfgobj()
  try:
    odbcfg,fname = fname
    odbcfg.dbconn = connect(fname)
    odbcfg.curs = dbconn.cursor()
    return odbcfg
  except:
    return None

def checktbl(dbcfg,tblstruct):
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
  dbcfg.curs.execute(dbtblck)
  dbtblstate = dbcfg.curs.fetchone()
  rstatus = 0
  if dbtblstate == None:
    rstatus = definetbl(dbcfg,tblstruct)
  return rstatus


def definetbl(dbcfg,tblstruct):
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
  try:
    carr = ["" for i in xrange(len(tblstruct)-1)]
    for k,val in tblstruct.iteritems():
      if k == 'tblname':
        continue
      carr[val['index']] = "%s %s %s"%(k,val['type'],val['nullst'])
  except:
    return -1
  try:
    dbctbl = "CREATE TABLE %s ( %s );"%(tblstruct['tlbname'],','.join(carr))
    dbcfg.curs.execute(dbctbl)
  except:
    return -2

