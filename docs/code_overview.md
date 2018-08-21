# Pavilion Code Overview

The purpose of this document is to give a brief overview of the current state of the Pavilion code
base, so that we can then plan its next evolution. This won't be kept up-to-date as changes are
made; if something doesn't match this document, it's probably new.

## PAV/modules

### basejobcontroller.py

Contains a the base class for running pavilion jobs, which looks to be a large portion of pavilion
itself.

_Generic Jobcontroller class_
  - job logging
  - source location (and working\_space) tracking
  - run cmd
  - pavilion environment setup
  - working space setup
  - build kickoff
  - query (noop)
  - start()
  - test epilog
  - cleanup
  - trend data

### gz2pv.py

Gazebo to Pavilion config converter stuff.

### helperutils.py

Contains a python `which` command.

### ldms.py

I don't know what this is for yet.

_LDMS class_

### makebaselines.py

Script to make result averages from get\_results data.

### makeboxplots.py

Script to max box plots from get\_results data.

### moabjobcontroller.py

_Subclass of JobController for MOAB jobs_
 - Has stuff for dealing with datawarp
 - Sets up pavilion environment

### rawjobcontroller.py

_Subclass of JobController for directly run jobs_
  - Not really much going on here

### slurmjobcontroller.py




