#!/usr/bin/env python

'''
dedt_dev.py
  A script isolating the dedt component of the PyLDFI workflow.
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!

# ............................................................................ #
if not os.path.abspath( __file__ + "/../../../src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../src" )  )

from utils import parseCommandLineInput, tools

# ............................................................................ #
if not os.path.abspath( __file__ + "/../../../lib/orik/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/orik/src" )  )

from dedt import dedt

# ............................................................................ #
# unit test framework
import Test_dedt_dev

# **************************************** #


##############
#  DEDT DEV  #
##############
# input a dedalus program from the command line
# output comparison status as true or false
# make sure dedt interpretter produces a correct c4 datalog representation.
def dedt_dev() :

  # ----------------------------------------------- #
  # delete any lingering dbs from previous run
  os.system( "rm IR.db" )

  # ----------------------------------------------- #
  # get dictionary of commandline arguments.
  # exits here if user provides invalid inputs.
  argDict = parseCommandLineInput.parseCommandLineInput( )

  # ----------------------------------------------- #
  # instantiate IR database
  saveDB = os.getcwd() + "/IR.db"
  IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor = IRDB.cursor()

  # ----------------------------------------------- #
  # run dedalus translator on the given input arguments
  programData = dedt.translateDedalus( argDict, cursor )

  # ----------------------------------------------- #
  # format results for std out

  programLines  = programData[0][0]
  programTables = programData[0][1]

  print
  print "======================="
  print "=  FINAL C4 PROGRAM   ="
  print "======================="
  print
  for line in programLines :
    print line
  print
  print "======================="
  print "======================="
  print
  print "==================="
  print "=  C4 TABLE LIST  ="
  print "==================="
  print programTables
  print
  print "==================="
  print "==================="
  print

  # ----------------------------------------------- #
  # delete any lingering dbs from previous run
  os.system( "rm IR.db" )


##################
#  TEST RESULTS  #
##################
# run unit tests
def testResults( ) :

  print
  print
  print "*****************************************************"
  print "**    RUNNING TEST SUITE FOR DEDALUS TRANSLATOR    **"
  print "*****************************************************"
  print

  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dedt_dev.Test_dedt_dev )
  return unittest.TextTestRunner( verbosity=2, buffer=True ).run( suite )


########################
# THREAD OF EXECUTION  #
########################

# run unit tests
if sys.argv[1] == "unittests" :
  testResults()

# run interactive tests
else :
  dedt_dev()



#########
#  EOT  #
#########
