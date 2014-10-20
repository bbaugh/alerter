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
try:
  import sys, re, time, logging, traceback
  from os import environ, path, _exit, makedirs, stat, access, R_OK, W_OK
  import argparse
except:
  print 'Failed to load base modules'
  _exit(-1)

try:
  from db_interface import *
except:
  print 'Failed to load db_interface'
  _exit(-1)


parser = argparse.ArgumentParser(description='Sending alerts.')


parser.add_argument("--cfg-file",\
                    action="store", dest="cfgfile", \
                    type=argparse.FileType('r'),\
                    help="Configuration file.")

parser.add_argument("--cfg-delimiter",\
                    action="store", dest="cfgdelimiter", \
                    default=':',\
                    help="Delimiter used in configuration file.")

parser.add_argument("--verbosity",\
                    action="store", dest="verbosity", \
                    default=30,\
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
    carr = line.split(delimiter)
    # Skipp badly formatted lines
    if len(carr) != 2:
      status += 1
      continue
    retdict[carr[0].strip()] = carr[1].strip()
  return retdict, status

def easy_exit(eval,dbcfgs):
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

def sendalerts(dbcfg,cfg,type,subject,text):
  start_time = int(time.time())
  # Don't send duplicate alerts
  ckalert = "SELECT * FROM %s WHERE start<%i AND type=%i;"
  ckalert%(cfg['tblname'],start_time,)
  dbcfg.curs.execute(ckalert)
  rstatus = []
  for calerts in cfg['alerters']:
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
  print cfg
  ##############################################################################
  # LOG FILE CONFIGURATION
  ##############################################################################
  # Log file name
  logging.basicConfig(filename=cfg['logfile'],\
            format='%(asctime)s %(levelname)s: %(message)s',\
            filemode='a', level=logging.DEBUG)
  #logging.setLevel(args.verbosity)
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
        logging.error('Failed to load email_alerts')
        easy_exit(-4)
    elif ctype == 'twitter':
      try:
        import twitter_alerts as ta
        cfg['alerters'].append(ea.twitter_alerts(cfg))
      except:
        logging.error('Failed to load twitter_alerts')
        easy_exit(-4)
    elif ctype == 'slack':
      try:
        import slack_alerts as sa
        cfg['alerters'].append(ea.slack_alerts(cfg))
      except:
        logging.error('Failed to load slack_alerts')
        easy_exit(-4)
    else:
      utypes.append(ctype)
  if len(utypes) != 0:
    logging.error('Unsupported alert types: %s'%(', '.join(utypes)))
    easy_exit(-4)
  ##############################################################################
  # Get Database
  ##############################################################################
  try:
    dbcfg = connectdb(cfg['dbfname'])
  except:
    logging.error('Could not read %s'%(cfg['dbfname']))
    easy_exit(-1,None)
  if dbcfg == None:
    logging.info('DB failed to initialize.')
    easy_exit(-1,None)
  tblstruct['tblname'] = cfg['tblname']
  tblstatus = checktbl(dbcfg,tblstruct)
  if tblstatus != 0:
    logging.error('Unable to create table in DB.')
    easy_exit(-1,dbcfg)
  ##############################################################################
  # Meat
  # Edit this area to perform check whatever is desired
  ##############################################################################
  send_alert = False
  ##############################################################################
  # send alert
  ##############################################################################
  if send_alert:
    astatus = sendalerts(dbcfg,cfg,1,'test alert',\
               'This is a test. This is only a test of the alert system.')
  ##############################################################################
  # clean up
  ##############################################################################
  easy_exit(0,[dbcfg])

