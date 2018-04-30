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
    self.interesting   = False


    # -------------------------------- #
    # grab settings configs

    self.num_filtering_configs = 0

    # +++++++++++++++ #
    #  TREE SIMPLIFY  #
    # +++++++++++++++ #
    try :
      self.TREE_SIMPLIFY = tools.getConfig( self.argDict[ "settings" ], \
                                                          "DEFAULT", \
                                                          "TREE_SIMPLIFY", \
                                                          bool )
    except ConfigParser.NoOptionError :
      self.TREE_SIMPLIFY = False
      logging.warning( "WARNING : no 'TREE_SIMPLIFY' defined in 'DEFAULT' section of " + \
                       self.argDict[ "settings" ] + "...running with TREE_SIMPLIFY==False." )
    logging.debug( "  FACT NODE : using TREE_SIMPLIFY = " + str( self.TREE_SIMPLIFY ) )

    # +++++++++++++ #
    #  CLOCKS_ONLY  #
    # +++++++++++++ #
    try :
      self.CLOCKS_ONLY = tools.getConfig( self.argDict[ "settings" ], \
                                          "DEFAULT", \
                                          "CLOCKS_ONLY", \
                                          bool )
      if self.CLOCKS_ONLY :
        self.num_filtering_configs += 1
    except ConfigParser.NoOptionError :
      self.CLOCKS_ONLY = False
      logging.warning( "WARNING : no 'CLOCKS_ONLY' defined in 'DEFAULT' section of " + \
                     self.argDict[ "settings" ] + "...running with CLOCKS_ONLY==False." )

    # ++++++++++++++++ #
    #  POS_FACTS_ONLY  #
    # ++++++++++++++++ #
    try :
      self.POS_FACTS_ONLY = tools.getConfig( self.argDict[ "settings" ], \
                                             "DEFAULT", \
                                             "POS_FACTS_ONLY", \
                                             bool )
      if self.POS_FACTS_ONLY :
        self.num_filtering_configs += 1
    except ConfigParser.NoOptionError :
      self.POS_FACTS_ONLY = False
      logging.warning( "WARNING : no 'POS_FACTS_ONLY' defined in 'DEFAULT' section of " + \
                     self.argDict[ "settings" ] + "...running with POS_FACTS_ONLY==False." )

    # ++++++++++++++++++++ #
    #  EXCLUDE_SELF_COMMS  #
    # ++++++++++++++++++++ #
    try :
      self.EXCLUDE_SELF_COMMS = tools.getConfig( self.argDict[ "settings" ], \
                                                 "DEFAULT", \
                                                 "EXCLUDE_SELF_COMMS", \
                                                 bool )
      if self.EXCLUDE_SELF_COMMS :
        self.num_filtering_configs += 1
    except ConfigParser.NoOptionError :
      self.EXCLUDE_SELF_COMMS = False
      logging.warning( "WARNING : no 'EXCLUDE_SELF_COMMS' defined in 'DEFAULT' section of " + \
                     self.argDict[ "settings" ] + "...running with EXCLUDE_SELF_COMMS==False." )

    # ++++++++++++++++++++++ #
    #  EXCLUDE_NODE_CRASHES  #
    # ++++++++++++++++++++++ #
    try :
      self.EXCLUDE_NODE_CRASHES = tools.getConfig( self.argDict[ "settings" ], \
                                                   "DEFAULT", \
                                                   "EXCLUDE_NODE_CRASHES", \
                                                   bool )
      if self.EXCLUDE_NODE_CRASHES :
        self.num_filtering_configs += 1
    except ConfigParser.NoOptionError :
      self.EXCLUDE_NODE_CRASHES = False
      logging.warning( "WARNING : no 'EXCLUDE_NODE_CRASHES' defined in 'DEFAULT' section of " + \
                     self.argDict[ "settings" ] + "...running with EXCLUDE_NODE_CRASHES==False." )


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
      return "fact->" + negStr + self.name + "(" + str(self.record) + ")"

    else :
      return "fact->" + self.name + "(" + str(self.record) + ")"


  ######################
  #  AM I INTERESTING  #
  ######################
  # check if this fact is interesting 
  # using heuristics
  def am_i_interesting( self ) :

    flag = 0

    if self.CLOCKS_ONLY and self.name.startswith( "clock" ) :
      flag += 1

    if self.POS_FACTS_ONLY and not self.isNeg :
      flag += 1

    if self.EXCLUDE_SELF_COMMS and not self.is_self_comm() :
      flag += 1

    if self.EXCLUDE_NODE_CRASHES and not self.is_node_crash() :
      flag += 1

    logging.debug( "  AM I INTERESTING : flag                       = " + str( flag ) )
    logging.debug( "  AM I INTERESTING : self.num_filtering_configs = " + str( self.num_filtering_configs ) )
    logging.debug( "  AM I INTERESTING : flag == self.num_filtering_configs = " + str( flag == self.num_filtering_configs ) )

    if flag >= self.num_filtering_configs :
      self.interesting = True

    logging.debug( "  AM I INTERESTING : self.name = " + self.name )
    logging.debug( "  AM I INTERESTING : conclusion : " + str( self.interesting ) )


  ##################
  #  IS SELF COMM  #
  ##################
  def is_self_comm( self ) :
    if not self.name == "clock" :
      return False
    else :
      if self.record[ 0 ] == self.record[ 1 ] :
        return True
      else :
        return False


  ###################
  #  IS NODE CRASH  #
  ###################
  def is_node_crash( self ) :
    if not self.name == "clock" :
      return False
    else :
      if self.record[ 1 ] == "_" :
        return True
      else :
        return False

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
