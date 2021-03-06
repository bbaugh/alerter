#!/usr/bin/env python
################################################################################
#  alerter.py
#  Sends alerts keeping track of them via sqlite db.
#  This is a simplified framework which should be modified for specific use
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
################################################################################
# Load needed modules
################################################################################
import sys, re, time, logging, traceback
from os import environ, path, _exit, makedirs, stat, access, R_OK, W_OK
import argparse

from db_interface import dbcfgobj



parser = argparse.ArgumentParser(description='Sending alerts.')


parser.add_argument("--cfg-file",\
                    action="store", dest="cfgfile", \
                    type=argparse.FileType('r'),\
                    help="Configuration file.")

parser.add_argument("--cfg-delimiter",\
                    action="store", dest="cfgdelimiter", \
                    default=':', type=str,\
                    help="Delimiter used in configuration file.")

parser.add_argument("--verbosity",\
                    action="store", dest="verbosity", \
                    default=30, type=int,\
                    help="Logging level:\n"\
                    +"  CRITICAL - 50\n"\
                    +"  ERROR - 40\n"\
                    +"  WARNING - 30\n"\
                    +"  INFO - 20\n"\
                    +"  DEBUG - 10\n")


args = parser.parse_args()

################################################################################
# Define DB structure
# This is the basic framework other structures can be used
################################################################################
'''
  tblstruct is a dictionary with the following entries:
  tblname - name of table to be created
  colname - colname can be anything other than tblname and is a
            dictonary containing:
            index - interger index
            type - data type to be stored
            nullst - null state
'''
tblstruct = {}
# Unix time stamp of start time REQUIRED
tblstruct['start'] = {}
tblstruct['start']['index']  = 0
tblstruct['start']['type']   = 'INT PRIMARY KEY'
tblstruct['start']['nullst'] = 'NOT NULL'
# integer type of alert REQUIRED
tblstruct['type'] = {}
tblstruct['type']['index']  = 1
tblstruct['type']['type']   = 'INT'
tblstruct['type']['nullst'] = 'NOT NULL'
# Unix time stamp of end time
tblstruct['end'] = {}
tblstruct['end']['index']  = 2
tblstruct['end']['type']   = 'INT'
tblstruct['end']['nullst'] = ''
# Unix time stamp of sent time
tblstruct['sent'] = {}
tblstruct['sent']['index']  = 3
tblstruct['sent']['type']   = 'INT'
tblstruct['sent']['nullst'] = ''

################################################################################
# Useful functions
################################################################################
def readcfg(cfgfile,delimiter):
  '''
    Reads in a configuraiton file formatted where each line contains a key and 
    a value separated by the provided delimiter. Returns a dictionary and 
    status integer. None zero status means incorrectly formatted file.
  '''
  retdict = {}
  status = 0
  for line in cfgfile:
    line = line.strip()
    # skip blank lines
    if len(line) == 0:
      continue
    # Skip comments
    if line[0] == '#':
      continue
    dloc = line.find(delimiter)
    # Skipp badly formatted lines
    if dloc < 0:
      status += 1
      continue
    retdict[line[:dloc].strip()] = line[dloc+1:].strip()
  return retdict, status

def easy_exit(eval,dbcfgs=None):
  '''
    Function to clean up before exiting and exiting itself
  '''
  if dbcfgs != None:
    nfailed = 0
    for dbcfg in dbcfgs:
      try:
        # Close DB connections
        dbcfg.curs.close()
        dbcfg.dbconn.commit()
      except:
        nfailed += 1
  _exit(eval)

def sendalerts(alrtrs,type,subject,text):
  rstatus = []
  for calerts in alrtrs:
    astatus = calerts.alert(subject,text)
    if astatus != 0:
      rstatus.append('%s failed to alert with: %i'%(calerts.type,astatus))
  return rstatus


if __name__ == "__main__":
  ##############################################################################
  # read config
  ##############################################################################
  cfg,cfgstatus = readcfg(args.cfgfile,args.cfgdelimiter)
  if cfgstatus != 0:
    print 'Configuration file incorrectly formatted.'
    easy_exit(-3)
  ##############################################################################
  # LOG FILE CONFIGURATION
  ##############################################################################
  # Log file name
  logfname = cfg['logfile']
  if logfname == "stdout":
    logfname = sys.stdout
  logger = logging.getLogger()
  logch = logging.StreamHandler(logfname)
  logfmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
  logch.setFormatter(logfmt)
  logch.setLevel(args.verbosity)
  logger.addHandler(logch)
  ##############################################################################
  # Check configuration now that we have logging in place
  ##############################################################################
  atypes = cfg['type'].split(',')
  utypes = []
  cfg['alerters'] = []
  for ctype in atypes:
    ctype = ctype.strip()
    if ctype == 'email':
      try:
        import email_alerts as ea
        cfg['alerters'].append(ea.email_alerts(cfg))
      except:
        logger.error('Failed to load email_alerts:\n%s'%traceback.format_exc())
        easy_exit(-4)
    elif ctype == 'twitter':
      try:
        import twitter_alerts as ta
        cfg['alerters'].append(ta.twitter_alerts(cfg))
      except:
        logger.error('Failed to load twitter_alerts:\n%s'%traceback.format_exc())
        easy_exit(-4)
    elif ctype == 'slack':
      try:
        import slack_alerts as sa
        cfg['alerters'].append(sa.slack_alerts(cfg))
      except:
        logger.error('Failed to load slack_alerts:\n%s'%traceback.format_exc())
        easy_exit(-4)
    else:
      utypes.append(ctype)
  if len(utypes) != 0:
    logger.error('Unsupported alert types: %s'%(', '.join(utypes)))
    easy_exit(-4)
  ##############################################################################
  # Get Database
  ##############################################################################
  dbcfg = dbcfgobj(cfg['dbfname'])
  if dbcfg == None:
    logger.info('DB failed to initialize.')
    easy_exit(-1,None)
  tblstruct['tblname'] = cfg['tblname']
  tblstatus = dbcfg.checktbl(tblstruct)
  if tblstatus != 0:
    logger.error('Unable to create table (%s) in DB:\n%s'%(tblstruct['tblname'],\
                                                           traceback.format_exc()))
    easy_exit(-1,dbcfg)
  ##############################################################################
  # Meat
  # Edit this area to perform check of whatever is desired
  ##############################################################################
  ctime = int(time.time())
  ctype = 2
  # Don't duplicate rows
  ckalert = "SELECT * FROM %s WHERE start<%i AND type=%i AND end is NULL;"
  ckalert = ckalert%(cfg['tblname'],ctime,ctype)
  # Example of closing all open rows
  for crw in dbcfg.curs.execute(ckalert):
    updtalert = "UPDATE %s SET end=%i WHERE start=%i and type=%i;"
    updtalert = updtalert%(cfg['tblname'],ctime,\
                           crw[tblstruct['start']['index']],ctype)
    dbcfg.curs.execute(updtalert)

  # Example of adding a new row
  insrtalert = "INSERT INTO %s(start,type) VALUES(%i,%i);"
  insrtalert = insrtalert%(cfg['tblname'],ctime,ctype)
  dbcfg.curs.execute(insrtalert)

  time.sleep(1) # let the clock tick
  send_alert = True # for testing always send the alert
  ##############################################################################
  # send alert
  ##############################################################################
  if send_alert:
    ctime = int(time.time())
    # Don't send duplicate alerts
    ckalert  = "SELECT * FROM %s WHERE start<%i AND type=%i AND end is NULL "
    ckalert += "AND sent is NULL;"
    ckalert = ckalert%(cfg['tblname'],ctime,ctype)
    # Example of sending messages and setting DB to sent
    setsnts = []
    for crw in dbcfg.curs.execute(ckalert):
      astatus = sendalerts(cfg['alerters'],ctype,'test alert',\
               'This is a test.\nThis is only a test of the <https://github.com/bbaugh/alerter|alerter system>.')
      setsnts.append([crw[tblstruct['start']['index']],ctype,ctime])
    for cs in astatus:
      logger.info(cs)
    for csnt in setsnts:
      # Example of updating a row
      updtalert = "UPDATE %s SET sent=%i WHERE start=%i and type=%i;"
      updtalert = updtalert%(cfg['tblname'],csnt[2],csnt[0],csnt[1])
      dbcfg.curs.execute(updtalert)

      
  ##############################################################################
  # clean up
  ##############################################################################
  easy_exit(0,[dbcfg])

