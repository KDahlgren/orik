#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, string, sys

# ------------------------------------------------------ #

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utils import tools

# **************************************** #


class SimpNode( ) :

  ################
  #  ATTRIBUTES  #
  ################
  label          = None  # name of relation identifier
  treeType       = None  # goal, rule, or fact
  isNeg          = None  # is goal negative?

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, label, treeType, isNeg ) :

    self.label    = label
    self.treeType = treeType
    self.isNeg    = isNeg


  ##############
  #  __STR __  #
  ##############
  def __str__( self ) :
    return "label = " + self.label + " : treeType = " + self.treeType + ", isNeg = " + str( self.isNeg )


#########
#  EOF  #
#########
