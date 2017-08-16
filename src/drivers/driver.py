#!/usr/bin/env python

'''
driver1.py
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!

import Core

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utils import parseCommandLineInput, tools

# **************************************** #


#############
#  GLOBALS  #
#############
DEBUG = tools.getConfig( "DRIVERS", "DRIVER_DEBUG", bool )

C4_DUMP_SAVEPATH  = os.path.abspath( __file__ + "/../../.." ) + "/save_data/c4Output/c4dump.txt"
TABLE_LIST_PATH   = os.path.abspath( __file__ + "/../.."    ) + "/evaluators/programFiles/" + "tableListStr.data"

# remove files from previous runs or else suffer massive file collections.
os.system( "rm " + os.path.abspath( __file__ + "/../../.." ) + "/save_data/graphOutput/*.png" )

############
#  DRIVER  #
############
def driver() :

  os.system( "rm IR.db" ) # delete db from previous run, if appicable

  # get dictionary of commandline arguments.
  # exits here if user provides invalid inputs.
  argDict = parseCommandLineInput.parseCommandLineInput( )  # get dictionary of arguments.

  # instantiate IR database
  saveDB = os.getcwd() + "/IR.db"
  IRDB   = sqlite3.connect( saveDB ) # database for storing IR, stored in running script dir
  cursor = IRDB.cursor()

  # initialize core
  c = Core.Core( argDict, cursor )

  # run orik on given spec (in file provided in argDict)
  c.run_workflow()

  os.system( "rm IR.db" ) # delete db from previous run, if appicable

  if DEBUG :
    "PROGRAM ENDED SUCESSFULLY."


#########################
#  THREAD OF EXECUTION  #
#########################
driver()


#########
#  EOF  #
#########
