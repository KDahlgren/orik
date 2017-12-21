#############
#  IMPORTS  #
#############
# standard python packages
import logging, os, sys

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #

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
