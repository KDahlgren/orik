#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import ConfigParser, copy, inspect, logging, os, sys
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
  def __init__( self, name="DEFAULT", isNeg=None, record=[], parsedResults={}, cursor=None, argDict = {} ) :

    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )
    logging.debug( "in FactNode.FactNode : " + name )
    logging.debug( "  name   = " + name )
    logging.debug( "  isNeg  = " + str( isNeg ) )
    logging.debug( "  record = " + str( record ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    self.argDict = {}
    self.argDict = argDict

    self.name          = name
    self.isNeg         = isNeg
    self.record        = record
    self.parsedResults = parsedResults
    self.cursor        = cursor
    self.uninteresting = False

    try :
      self.TREE_SIMPLIFY = tools.getConfig( self.argDict[ "settings" ], "DEFAULT", "TREE_SIMPLIFY", bool )
    except ConfigParser.NoOptionError :
      self.TREE_SIMPLIFY = False
      logging.warning( "WARNING : no 'TREE_SIMPLIFY' defined in 'DEFAULT' section of " + \
                       self.argDict[ "settings" ] + "...running with TREE_SIMPLIFY==False." )
    logging.debug( "  FACT NODE : using TREE_SIMPLIFY = " + str( self.TREE_SIMPLIFY ) )

    # -------------------------------- #
    # make sure this is actually a 
    # fact.

    if not self.is_fact() :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : relation '" + self.name + "' does not reference a fact. aborting." )

    # -------------------------------- #
    # determine whether this fact is interesting

    self.am_i_interesting()

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
      if self.TREE_SIMPLIFY == True and self.uninteresting == True :
        return "fact->__UNINTERESTING__" + negStr + self.name + "(" + str(self.record) + ")"
      else :
        return "fact->" + negStr + self.name + "(" + str(self.record) + ")"

    else :
      if self.TREE_SIMPLIFY == True and self.uninteresting == True :
        return "fact->__UNINTERESTING__" + self.name + "(" + str(self.record) + ")"
      else :
        return "fact->" + self.name + "(" + str(self.record) + ")"


  ######################
  #  AM I INTERESTING  #
  ######################
  # check if this fact is interesting 
  # using heuristics
  def am_i_interesting( self ) :

    # only clock facts are interesting
    if self.isNeg or not self.name.startswith( "clock" ) :
      self.uninteresting = True

#    # negative facts are not interesting.
#    if self.isNeg :
#      self.uninteresting = True


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
