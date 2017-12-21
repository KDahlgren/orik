#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, pydot, sys

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #

C4_RESULTS_PATH = os.path.abspath( __file__ + "/../../../save_data/c4Output/c4dump.txt" )

#################
#  CREATE NODE  #
#################
def createNode( nodeToAdd ) :

  if nodeToAdd.treeType == "goal" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='oval' )

  elif nodeToAdd.treeType == "rule" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='box' )

  elif nodeToAdd.treeType == "fact" :
    thisNode = pydot.Node( str( nodeToAdd ), shape='cylinder' )

  else :
    sys.exit( "********************\n********************\nFATAL ERROR in file " + __name__ + " in function " + inspect.stack()[0][3] + " :\nUnrecognized treeType" + str( nodeToAdd.treeType ) )

  return thisNode


#########
#  EOF  #
#########
