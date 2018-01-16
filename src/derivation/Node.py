#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, pydot, sys

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
  def __init__( self, treeType = None, \
                      name     = None, \
                      isNeg    = None, \
                      record   = [], \
                      results  = {}, \
                      cursor   = cursor ) :

    self.treeType = treeType
    self.name     = name
    self.isNeg    = isNeg
    self.record   = record
    self.results  = results
    self.cursor   = cursor


#########
#  EOF  #
#########
