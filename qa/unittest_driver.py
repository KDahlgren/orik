#!/usr/bin/env python

import logging, os, sys, unittest
import Test_derivation, Test_derivation_functionality

#####################
#  UNITTEST DRIVER  #
#####################
def unittest_driver() :

  print
  print "*********************************"
  print "*  RUNNING TEST SUITE FOR ORIK  *"
  print "*********************************"
  print

  # make absolutely sure no leftover IR files exist.
  if os.path.exists( "./IR*.db*" ) :
    os.system( "rm ./IR*.db*" )
    logging.info( "  UNIT TEST DRIVER : deleted all rogue IR*.db* files." )

  # need to run these individually or else
  # failures in bulk. weird.
  test_list = [

    "test_prov_tree_1", \
    "test_prov_tree_2", \
    "test_prov_tree_3", \
    "test_prov_tree_4", \
    "test_prov_tree_5", \
    "test_prov_tree_6", \
    "test_prov_tree_7", \
    "test_prov_tree_8", \
    "test_example_1", \
    "test_example_2", \
    "test_dm_demo_1", \
    "test_simplog", \
    "test_rdlog", \
    "test_replog", \
    "test_simplog_dm", \
    "test_rdlog_dm", \
    "test_replog_dm"

  ]

  custom_runner( test_list )

  # run Test_derivation_functionality tests
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_derivation_functionality.Test_derivation_functionality )
  unittest.TextTestRunner( verbosity=2, buffer=True ).run( suite )


###################
#  CUSTOM RUNNER  #
###################
def custom_runner( test_list ) :
  for test in test_list :
    os.system( "python -m unittest Test_derivation.Test_derivation." + test )


#########################
#  THREAD OF EXECUTION  #
#########################
if __name__ == "__main__" :
  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  unittest_driver()

# make absolutely sure no leftover IR files exist.
if os.path.exists( "./IR*.db*" ) :
  os.system( "rm ./IR*.db*" )
  logging.info( "  UNIT TEST DRIVER : deleted all rogue IR*.db* files." )



#########
#  EOF  #
#########
