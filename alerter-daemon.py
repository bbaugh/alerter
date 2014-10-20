#!/usr/bin/env python
################################################################################
#  alerter-daemon.py
#
#  Script daemonizes sending of alerts.
#
#  Created by Brian Baughman on 2014-10-16.
#  Copyright 2014 Brian Baughman. All rights reserved.
################################################################################
try:
  import sys, re, time
  from daemon import runner
  from os import environ, path, _exit, makedirs, stat, devnull, access, X_OK
  from subprocess import call, STDOUT, PIPE, Popen
  import argparse
  pathname = path.dirname(sys.argv[0])
except:
  print 'Failed to load base modules'
  sys.exit(-1)


parser = argparse.ArgumentParser(description='Creates a daemon for sending alerts.')


parser.add_argument("--inter",\
                    action="store", dest="inter", \
                    default=60,\
                    help="Number of seconds to wait between polls.")

parser.add_argument("--pid-file",\
                    action="store", dest="pidfile", \
                    default='/tmp/.alerter-daemon.lock',\
                    help="Lock file for daemon.")

parser.add_argument("--exec-fiile",\
                    action="store", dest="execfile", \
                    default='%s/alerter.py'%(pathname),\
                    help="Executable file to be run by daemon.")

parser.add_argument("--log-fiile",\
                    action="store", dest="logfile", \
                    default='/dev/null',\
                    help="Log file for daemon.")

args = parser.parse_args()



if not path.isfile(args.execfile):
  print 'Cannot find file: %s'%(args.execfile)
  _exit(-1)

if not access(args.execfile,X_OK):
  print 'Cannot execute : '%(args.execfile)
  _exit(-1)

################################################################################
# App to run
################################################################################

class App():
  def __init__(self, execfile, log, inter, pidfile):
    self.stdin_path = '/dev/null'
    self.stdout_path = log
    self.stderr_path = log
    self.pidfile_path =  pidfile
    self.pidfile_timeout = inter+1
    self.umask = 0022
    self.inter = inter
    self.execfile = execfile
    self.modtime = None
  
  def run(self):
    self.Check()

  
  def Alerter(self):
    '''
      Calls execfile
    '''
    call([self.execfile])

  def Check(self):
    '''
      Function which calls itself every interval
    '''
    self.Alerter()
    # Wait for inter then call again
    time.sleep(self.inter)
    self.Check()


# Start daemon
if __name__ == "__main__":
  app = App(execfile=args.execfile, log=args.logfile, inter=args.inter, \
            pidfile=args.pidfile)
  daemon_runner = runner.DaemonRunner(app)
  daemon_runner.daemon_context.files_preserve=[args.logfile]
  daemon_runner.do_action();

