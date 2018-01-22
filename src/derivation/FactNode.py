#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import copy, inspect, logging, os, sys
from Node import Node

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #

class FactNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################

  treeType    = "fact"


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name="DEFAULT", isNeg=None, record=[], parsedResults={}, cursor=None ) :

    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )
    logging.debug( "in FactNode.FactNode : " + name )
    logging.debug( "  name   = " + name )
    logging.debug( "  isNeg  = " + str( isNeg ) )
    logging.debug( "  record = " + str( record ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    self.name          = name
    self.isNeg         = isNeg
    self.record        = record
    self.parsedResults = parsedResults
    self.cursor        = cursor


    # -------------------------------- #
    # make sure this is actually a 
    # fact.

    if not self.is_fact() :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : relation '" + self.name + "' does not reference a fact. aborting." )


    # -------------------------------- #
    # initialize node object

    Node.__init__( self, self.treeType, \
                         self.name, \
                         self.isNeg, \
                         self.record, \
                         self.parsedResults, \
                         self.cursor )


  #############
  #  __STR__  #
  #############
  # the string representation of a FactNode
  def __str__( self ) :

    if self.isNeg :
      negStr = "_NOT_"
      return "fact->" + negStr + self.name + "(" + str(self.record) + ")"

    else :
      return "fact->" + self.name + "(" + str(self.record) + ")"


  #############
  #  IS FACT  #
  #############
  # make sure this is actually a fact in the database.
  def is_fact( self ) :

    if self.name == "clock" or self.name == "next_clock" or self.name == "crash" :
      return True

    self.cursor.execute( "SELECT fid \
                          FROM   Fact \
                          WHERE  name=='" + self.name + "'" )
    fid_list = self.cursor.fetchall()
    fid_list = tools.toAscii_list( fid_list )

    logging.debug( "  IS FACT : fid_list = " + str( fid_list ) )

    # if this is a negative fact, just make sure the relation exists
    if self.isNeg :
      if len( fid_list ) > 0 :
        return True
      else :
        return False

    else :
      for fid in fid_list :
        self.cursor.execute( "SELECT dataID,data,dataType \
                              FROM   FactData \
                              WHERE  fid=='" + fid + "'" )
        data_list = self.cursor.fetchall()
        data_list = tools.toAscii_multiList( data_list )
        fact      = []
        for d in data_list :
          data     = d[1]
          dataType = d[2]
          if dataType == "int" :
            fact.append( data )
          else :
            data = data.replace( "'", "" )
            data = data.replace( '"', '' )
            fact.append( data )
  
        logging.debug( "fact        = " + str( fact ) )
        logging.debug( "self.record = " + str( self.record ) )
        logging.debug( "fact == self.record is " + str( fact == self.record ) )
  
        #if fact == self.record : # does not handle wildcards
        if self.is_match( fact ) :
          return True

    return False # otherwise, return false


  ##############
  #  IS MATCH  #
  ##############
  # check if the input fact 'matches' the record for this fact node.
  def is_match( self, fact ) :

    for i in range( 0, len( self.record ) ) :

      fact_datum   = fact[ i ]
      record_datum = self.record[ i ]

      # remove any quotes
      if record_datum.startswith( "'" ) and record_datum.endswith( "'" ) :
        record_datum = record_datum.replace( "'", "" )
      elif record_datum.startswith( '"' ) and record_datum.endswith( '"' ) :
        record_datum = record_datum.replace( '"', "" )

      if record_datum == "_" :
        pass
      else :
        if not fact_datum == record_datum :
          return False

    return True


#########
#  EOF  #
#########
