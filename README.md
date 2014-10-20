alerter
==========

Basic alerting framework for sending:

* emails
* slacks
* tweets

Via a periodic checking daemon or outside trigger.
Alerts are categorized and recorded.
Example alerter.py currently checks the DB and ends any open alerts of the
same type, creates a new alert row, sends alerts, updates DB with new sent
time. This files should be edited for the particular user cases.
