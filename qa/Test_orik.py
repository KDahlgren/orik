#!/usr/bin/env python

'''
Test_orik.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../../src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../src" ) )

from dedt  import dedt, dedalusParser, clockRelation, dedalusRewriter

if not os.path.abspath( __file__ + "/../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../lib/iapyx/src" ) )

from dedt  import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import dumpers, globalCounters, tools

# ------------------------------------------------------ #


###############
#  TEST ORIK  #
###############
class Test_orik( unittest.TestCase ) :

  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  ###############
  #  
  ###############
  # tests ???
  #@unittest.skip( "working on different example" )
  def test_( self ) :
    return None


#########
#  EOF  #
#########
