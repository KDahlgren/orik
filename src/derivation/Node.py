#############
#  IMPORTS  #
#############
# standard python packages
import os, sys

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utils import tools

# **************************************** #

DEBUG = tools.getConfig( "DERIVATION", "NODE_DEBUG", bool )

class Node( object ) :

  #############
  #  ATTRIBS  #
  #############
  treeType = None
  name     = None  # name of relation identifier
  isNeg    = None
  record   = []
  results  = None
  cursor   = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, treeType, name, isNeg, record, results, cursor ) :
    self.treeType = treeType
    self.name     = name
    self.isNeg    = isNeg
    self.record   = record
    self.results  = results
    self.cursor   = cursor


#########
#  EOF  #
#########
