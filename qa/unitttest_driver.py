#!/usr/bin/env python

import logging, os, unittest
import Test_derivation

#####################
#  UNITTEST DRIVER  #
#####################
def unittest_driver() :

  print
  print "***************************************"
  print "*  RUNNING TEST SUITE FOR DERIVATION  *"
  print "***************************************"
  print

  # make absolutely sure no leftover IR files exist.
  if os.path.exists( "./IR.db" ) :
    os.system( "rm ./IR.db" )
    logging.info( "  UNIT TEST DRIVER : deleted rogue IR.db file." )

  # run Test_derivation tests
  suite = unittest.TestLoader().loadTestsFromTestCase( Test_derivation.Test_derivation )
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
