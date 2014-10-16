#!/usr/bin/env python
################################################################################
#  base-alert.py
#  Checks status of computers and sends alerts keeping track of them via
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
except:
  print 'Failed to load base modules'
  _exit(-1)
try:
  try:
    from sqlite3 import connect
  except:
    try:
      from sqlite import connect
    except:
      sys.exit(-2)
  from email import MIMEText
  import smtplib
  # Home directory
  homedir = environ['HOME']
  # stop if something looks wrong
except:
  print 'Failed to load modules'
  sys.exit(-1)

##############################################################################
# Generic Settings
##############################################################################
# environmental variables prefix
eprfx = 'CR'
# base filename
bfnm = 'base-alert'
# Update date format
updfmt = '%Y-%m-%dT%H:%M:%S'
# Subject of email format
sbjctfmt = '%i computers not reporting'
# Content of email format
txtfmt = 'The following %i computers are not reporting:\n%s'

################################################################################
# Define DB structure
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
  dbtblck = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"%tblname
  dbcfg.curs.execute(dbtblck)
  dbtblstate = curs.fetchone()
  if dbtblstate == None:
    definetbl(dbcfg,tblstruct)


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


################################################################################
# Useful functions
################################################################################
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

def dircheck(dir):
  '''
    Checks if the given directory exists, if not it attempts to create it.
    '''
  try:
    stat(dir)
  except:
    makedirs(dir)
  try:
    stat(dir)
    return True
  except:
    return False

def gettxt(cinfo,curzen,sitetag,sitelink):
  '''
    Generated formatted text for email alert
  '''
  txt = txtfmt%(cinfo.inst.capitalize(),\
                cinfo.trigid,\
                curzen,\
                shorten(cinfo.link),\
                sitelink)
  return txt

def email(sender,recipient,subject,text):
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
  s = smtplib.SMTP(gcnsmtp)
  s.sendmail(sender, msg['To'].split(','), msg.as_string())
  s.quit()

if __name__ == "__main__":
  # Alerts config
  try:
    cfgfname = environ[eprfx+'CONFIGFILE']
  except:
    cfgfname = '%s/.%s.cfg'%(homedir,bfnm)

  # Log file name
  try:
    logfname = environ[eprfx+'LOGFILE']
  except:
    logfname = '%s/logs/%s.log'%(homedir,bfnm)

  # sqlite database file
  try:
    dbfname = environ['DBFNAME']
  except:
    dbfname = '%s/%s.db'%(homedir,bfnm)
  try:
    dbtablename = environ[eprfx+'TABLENAME']
  except:
    dbtablename = eprfx



  ##############################################################################
  # LOG FILE CONFIGURATION
  ##############################################################################
  # Log file name
  logging.basicConfig(filename=salertlog,\
                      format='%(asctime)s %(levelname)s: %(message)s',\
                      filemode='a', level=logging.DEBUG)
  ##############################################################################
  # Get Database
  ##############################################################################
  try:
    dbcfg = connectdb(dbfname)

  except:
    logging.error('Could not read %s'%dbfname)
    easy_exit(-1,None)
  if dbcfg == None:
    logging.info('DB failed to initialize.')
    easy_exit(-1,None)

  ##############################################################################
  # read config
  ##############################################################################
  # Sender of emails
  sender = None
  # Reciepents of email
  recipients = None
  # Read configuration file
  try:
    cfgif = open(cfgfname,'r')
    cfglines = cfgif.readlines()
    cfgif.close()
    if len(cfglines) >= 2:
      sender = cfglines[0].strip()
      recipients = cfglines[1].strip().split(',')
    if len(recipients) <=0 :
      sender = None
      recipients = None
  except:
    logging.error('Cannot read sender/recipients from: %s\n%s\n'%(cfgfname,traceback.format_exc()))
    easy_exit(-3,[dbcfg])

  ##############################################################################
  # Environment Settings
  ##############################################################################

  ################################################################################
  # Meat
  ################################################################################

  # Grab recents
  trig_tjd = 0
  trig_sod = 1
  id = 2
  trigid = 3
  updated_date = 4
  recentstr = "SELECT DISTINCT trig_tjd,trig_sod,id,trigid,updated_date"
  recentstr += " FROM %s ORDER BY trig_tjd DESC, trig_sod DESC LIMIT %i ;"%(dbcfg.dbname,\
                                                              nrecent)
  dbcfg.curs.execute(recentstr)
  recent = dbcfg.curs.fetchall()

  # XML header
  root = ET.Element("xml")
  root.attrib['version'] = "1.0"
  gcns = ET.SubElement(root, "gcns")

  a_id = alertdbcfg.dbstruct['id']['index']
  a_sent = alertdbcfg.dbstruct['sent']['index']
  a_updated_date = alertdbcfg.dbstruct['updated_date']['index']
  for row in recent:
    # Check if this entry has been updated
    upd = False
    sentflg = 0
    qstr = "SELECT * FROM %s WHERE trig_tjd=%s AND trigid='%s';"
    qstr = qstr%(alertdbcfg.dbname,row[trig_tjd],row[trigid])
    alertdbcfg.curs.execute(qstr)
    camtchs = alertdbcfg.curs.fetchall()
    if  len(camtchs) == 0:
      '''
        Add new entry
      '''
      nAlert = alertinfo()
      nAlert.trigid = row[trigid]
      nAlert.trig_tjd = row[trig_tjd]
      nAlert.trig_sod = row[trig_sod]
      nAlert.updated_date = row[updated_date]
      nAlert.sent = 0
      carr = [nAlert.__getattribute__(cattr) for cattr in alertdbcfg.dbstruct.keys() ]
      cintstr = alertdbcfg.inststr%tuple(carr)
      alertdbcfg.curs.execute(cintstr)
      alertdbcfg.dbconn.commit()
      alertdbcfg.curs.execute(qstr)
      camtchs = alertdbcfg.curs.fetchall()
      upd = True
    elif len(camtchs) > 1:
      '''
        This should never happen so assume it is an error and skip
      '''
      logging.info('Found multiple entries for %s'%row[trigid])
      continue
    rEUD = datetime.strptime(str(row[updated_date]),updfmt)
    for m in camtchs:
      mEUD =  datetime.strptime(str(m[a_updated_date]),updfmt)
      if rEUD > mEUD:
        upd = True
      sentflg += m[a_sent]

    # Calculate position at site
    qstr = "SELECT * FROM %s WHERE id=%s;"%(dbcfg.dbname,row[id])
    dbcfg.curs.execute(qstr)
    cmtchs = dbcfg.curs.fetchall()
    curinfo = MakeEntry(cmtchs[0],gcninfo,dbcfg.dbstruct)

    evtTime = tjd2dttm(curinfo.trig_tjd + curinfo.trig_sod/secInday)
    evtRA = deg2rad(float(curinfo.ra))
    evtDec = deg2rad(float(curinfo.dec))
    evtAlt,evtAz = eq2horz(obslat,obslon,evtTime,evtRA,evtDec)
    evtdZenith = 90. - rad2deg(evtAlt)
    if upd:
      logging.debug("Updated %s"%(curinfo.trigid))
      ustr = "UPDATE %s SET updated_date='%s' WHERE id='%s';"
      ustr = ustr%(alertdbcfg.dbname, row[updated_date], camtchs[0][a_id])
      try:
        alertdbcfg.curs.execute(ustr)
        alertdbcfg.dbconn.commit()
      except:
        logging.error( 'Failed to update Alert DB:\n%s'%traceback.format_exc())

    if evtdZenith < obshorizon and sentflg == 0:
      sbjct = sbjctfmt%(evtTime.strftime("%Y-%m-%d %H:%M:%S"),evtdZenith)
      txt = gettxt(curinfo,evtdZenith,sitetag,sitelink)
      ustr = "UPDATE %s SET sent=1 WHERE id='%s';"%(alertdbcfg.dbname,\
                                                     camtchs[0][a_id])
      try:
        alertdbcfg.curs.execute(ustr)
        alertdbcfg.dbconn.commit()
        email(sender,recipients,sbjct,txt)
        logging.info( 'Sent: %s'%(sbjct))
      except:
        logging.error( 'Failed to send notification or update Alert DB:\n%s'%traceback.format_exc())
        continue


    #Save to XML
    curgcn = ET.SubElement(gcns, "gcn")
    for cattr in dbcfg.dbstruct.keys():
      cursubelm = ET.SubElement(curgcn,cattr)
      cursubelm.text = str(curinfo.__getattribute__(cattr))
    cursubelm = ET.SubElement(curgcn,'trig_date')
    utt = evtTime.utctimetuple()
    cursubelm.text = "%i-%02i-%02i %02i:%02i:%02i"%(utt.tm_year,utt.tm_mon,\
                                                    utt.tm_mday,\
                                                    utt.tm_hour,utt.tm_min,\
                                                    utt.tm_sec)


  # Save XML
  logging.info( 'Updating XML')
  xmlfname = '%s/gcns.xml'%gcnweb
  fout = open(xmlfname,'w')
  if fout.closed:
    logging.error( 'Failed to open output XML file: %s'%(xmlfname))
    easy_exit(-6,[dbcfg,alertdbcfg])
  try:
    root.write(fout,pretty_print=True)
    fout.close()
  except:
    try:
      outtxt = ET.tostring(root)
      fout.write(outtxt)
      fout.close()
    except:
      fout.close()
      logging.error( 'Failed to open output XML file: %s'%(xmlfname))
      easy_exit(-6,[dbcfg,alertdbcfg])

  # Close DB connections
  dbcfg.curs.close()
  dbcfg.dbconn.commit()
  # Remove lock
  easy_exit(0,[dbcfg,alertdbcfg])

