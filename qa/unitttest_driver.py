#!/usr/bin/env python

import logging, os, string, sys, unittest
import Test_dedt, Test_dml, Test_vs_molly

#####################
#  UNITTEST DRIVER  #
#####################
def unittest_driver() :

  print
  print "***********************************"
  print "*   RUNNING TEST SUITE FOR ORIK   *"
  print "***********************************"
  print

  # make absolutely sure no leftover IR files exist.
  if os.path.exists( "./IR.db" ) :
    os.system( "rm ./IR.db" )
    logging.info( "  UNIT TEST DRIVER : deleted rogue IR.db file." )


  # run Test_orik tests
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_dedt.Test_dedt )
  unittest.TextTestRunner( verbosity=2, buffer=True ).run( suite )


#########################
#  THREAD OF EXECUTION  #
#########################
unittest_driver()

# make absolutely sure no leftover IR files exist.
if os.path.exists( "./IR.db" ) :
  os.system( "rm ./IR.db" )
  logging.info( "  UNIT TEST DRIVER : deleted rogue IR.db file." )



#########
#  EOF  #
#########
