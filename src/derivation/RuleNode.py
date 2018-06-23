#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import ConfigParser, copy, inspect, logging, os, string, sys
from Node import Node

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #

class RuleNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################

  treeType = "rule"
  ops  = [ "+", "-", "*", "/" ]
  aggs = [ "max<", "min<", "sum<", "count<", "avg<" ]

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, rid=None, name="DEFAULT", record=[], parsedResults={}, cursor=None, argDict={} ) :

    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )
    logging.debug( "in RuleNode.RuleNode : " + name )
    logging.debug( "  rid    = " + str( rid ) )
    logging.debug( "  record = " + str( record ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    self.argDict = {}

    self.rid             = rid
    self.name            = name
    self.record          = record
    self.parsedResults   = parsedResults
    self.cursor          = cursor
    self.argDict         = argDict

    # array of metadata for node descendants.
    # [ { 'treeType'      : "goal" | "fact",
    #     'node_name'     : <string>,
    #     'triggerRecord' : <string>,
    #     'polarity'      : "notin" | "",
    #   }, ... ]
    self.descendant_meta = [] # make sure this is empty.

    # -------------------------------- #
    # initialize node object

    Node.__init__( self, treeType = self.treeType, \
                         name     = self.name, \
                         record   = self.record, \
                         results  = self.parsedResults, \
                         cursor   = self.cursor )

    # -------------------------------- #
    # generate descendant meta data

    self.generate_descendant_meta()

    logging.debug( "===================================" )
    logging.debug( "  RULE NODE CONSTRUCTOR : " )
    logging.debug( "    self.rid           = " + str( self.rid ) )
    logging.debug( "    self.name          = " + str( self.name ) )
    logging.debug( "    self.record        = " + str( self.record ) )
    logging.debug( "    descendant_meta :" )
    for d in self.descendant_meta :
      logging.debug( "      d = " + str( d ) )
    logging.debug( "===================================" )


  #############
  #  __STR__  #
  #############
  # the string representation of a RuleNode
  def __str__( self ) :
    return "rule->" + self.name + "(" + str(self.record) + ")"


  ##############################
  #  GENERATE DESCENDANT META  #
  ##############################
  # generate the meta data required to spawn the desendant goal or fact nodes.
  #
  # array of metadata for node descendants.
  # [ { 'treeType'      : "goal" | "fact",
  #     'node_name'     : <string>,
  #     'triggerRecord' : <string>,
  #     'polarity'      : "notin" | "",
  #   }, ... ]
  #
  def generate_descendant_meta( self ) :

    # -------------------------------- #
    # get the list of goal attributes 

    self.cursor.execute( "SELECT attName \
                          FROM   GoalAtt \
                          WHERE  rid=='" + str( self.rid ) + "'" )

    goal_atts = self.cursor.fetchall()
    goal_atts = tools.toAscii_list( goal_atts )

    logging.debug( "  GENERATE DESCENDANT META : rid       = " + self.rid )
    logging.debug( "  GENERATE DESCENDANT META : goal_atts = " + str( goal_atts ) )

    # -------------------------------- #
    # relate goal atts to data 
    # from record

    gatt_to_data = {}

    for i in range( 0, len( goal_atts ) ) :
      gatt                 = goal_atts[ i ]

      # handle goal attributes containing aggregate operators
      if self.contains_op( gatt ) :
        op         = self.get_op( gatt )
        lhs        = self.get_lhs( gatt )
        clean_gatt = self.get_clean_gatt( gatt )
        raw_data   = self.record[ i ]

        if op == "+" :
          real_data = str( int( raw_data ) - int( lhs ) )
        elif op == "-" :
          real_data = str( int( raw_data ) + int( lhs ) )
        elif op == "*" :
          real_data = str( int( raw_data ) / int( lhs ) )
        elif op == "/" :
          real_data = str( int( raw_data ) * int( lhs ) )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : unrecognized op '" + op + "'" )

        gatt_to_data[ clean_gatt ] = real_data

      # handle goal attributes containing aggregate functions
      elif self.contains_agg( gatt ) :
        op         = self.get_op( gatt )
        lhs        = self.get_lhs( gatt )
        clean_gatt = self.get_clean_gatt( gatt )
        raw_data   = self.record[ i ]

        gatt_to_data[ clean_gatt ] = raw_data

      else :
        data                 = self.record[ i ]
        gatt_to_data[ gatt ] = data

    logging.debug( "  GENERATE DESCENDANT META : gatt_to_data = " + str( gatt_to_data ) )

    # -------------------------------- #
    # get the list of subgoal names 
    # and polarities for each 
    # provenance rule.

    self.cursor.execute( "SELECT sid,subgoalName,subgoalPolarity \
                          FROM   Subgoals \
                          WHERE  rid=='" + str( self.rid ) + "'" )

    subgoal_list = self.cursor.fetchall()
    subgoal_list = tools.toAscii_multiList( subgoal_list )

    sid_to_name_and_polarity = {}

    for sub in subgoal_list :
      sid                             = sub[0]
      subgoalName                     = sub[1]
      subgoalPolarity                 = sub[2]
      sid_to_name_and_polarity[ sid ] = [ subgoalName, subgoalPolarity ]

    logging.debug( "  GENERATE DESCENDANT META : sid_to_name_and_polarity = " + str( sid_to_name_and_polarity ) )

    # -------------------------------- #
    # remove subgoal duplicates

    tmp  = {}
    tmp2 = {}
    for sid in sid_to_name_and_polarity :
      tmp[ str( sid_to_name_and_polarity[ sid ] ) ] = sid
    for subgoalInfo in tmp :
      array_str = subgoalInfo.translate( None, string.whitespace ) 
      array_str = array_str.replace( "[", "" )
      array_str = array_str.replace( "]", "" )
      array_str = array_str.replace( "'", "" )
      tmp2[ tmp[ subgoalInfo ] ] = array_str.split( "," )

    sid_to_name_and_polarity = copy.copy( tmp2 )
    logging.debug( "  GENERATE DESCENDANT META : sid_to_name_and_polarity (after de-pulication) = " + str( sid_to_name_and_polarity ) )

    # -------------------------------- #
    # get the attribute list
    # per subgoal

    sid_to_subgoal_att_list = {}

    for sid in sid_to_name_and_polarity :

      self.cursor.execute( "SELECT attID,attName \
                            FROM   SubgoalAtt \
                            WHERE  rid=='" + str( self.rid ) + "' \
                            AND    sid=='" + str( sid )      + "'" )

      satt_list                      = self.cursor.fetchall()
      satt_list                      = tools.toAscii_multiList( satt_list )
      satt_list_atts_only            = [ satt[1] for satt in satt_list ]
      sid_to_subgoal_att_list[ sid ] = satt_list

    logging.debug( "  GENERATE DESCENDANT META : sid_to_subgoal_att_list = " + str( sid_to_subgoal_att_list ) )

    # -------------------------------- #
    # create one descendant per 
    # subgoal
    #
    # { 'treeType'      : "goal" | "fact",
    #   'node_name'     : <string>,
    #   'triggerRecord' : <string>,
    #   'polarity'      : "notin" | "",
    # }

    for sid  in sid_to_name_and_polarity :

      subgoalName     = sid_to_name_and_polarity[ sid ][ 0 ]
      subgoalPolarity = sid_to_name_and_polarity[ sid ][ 1 ]

      logging.debug( "  GENERATE DESCENDANT META : subgoalName     = " + subgoalName )
      logging.debug( "  GENERATE DESCENDANT META : subgoalPolarity = " + subgoalPolarity )

      if subgoalName.startswith( "domcomp_" ) or \
         subgoalName.startswith( "dom_" )     or \
         subgoalName.startswith( "unidom_" )  or \
         subgoalName.startswith( "exidom_" )  or \
         subgoalName.startswith( "orig_" ) :
        logging.debug( "  GENERATE DESCENDANT META : hit a " + subgoalName + " descendant. skipping creation... "  )
        pass
      else :
        subgoal_type_data = self.check_subgoal_type( subgoalName )
        is_edb            = subgoal_type_data[ 0 ]
        is_idb            = subgoal_type_data[ 1 ]

        logging.debug( "  GENERATE DESCENDAT META : is_edb := " + str( is_edb ) )
        logging.debug( "  GENERATE DESCENDAT META : is_idb := " + str( is_idb ) )

        # -------------------------------- #
        # CASE : subgoal is edb only, 
        #        so spawn fact

        if is_edb and not is_idb :
          treeType = "fact"

        # -------------------------------- #
        # CASE : subgoal is idb only, 
        #        so spawn goal

        elif not is_edb and is_idb :
          treeType = "goal"

        # -------------------------------- #
        # CASE : subgoal is both idb and 
        #        edb, so break b/c ambiguous

        elif is_edb and is_idb :
          tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : subgoal '" + subgoalName + "' is both edb and idb. ambiguous. aborting." )

        # -------------------------------- #
        # CASE : subgoal is neither idb 
        #        nor edb, so break b/c 
        #        something's wrogn

        else :
          tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : subgoal '" + subgoalName + "' is neither edb nor idb. aborting." )


        # -------------------------------- #
        # get remaining data

        node_name = subgoalName
        polarity  = subgoalPolarity
        record    = self.get_trigger_record_for_subgoal( gatt_to_data, sid_to_subgoal_att_list[ sid ] )

        d = {}
        d[ "treeType" ]      = treeType
        d[ "node_name" ]     = node_name
        d[ "triggerRecord" ] = record
        d[ "polarity" ]      = polarity

        try :
          TREE_SIMPLIFY = tools.getConfig( self.argDict[ "settings" ], "DEFAULT", "TREE_SIMPLIFY", bool )
        except ConfigParser.NoOptionError :
          TREE_SIMPLIFY = False
          logging.warning( "WARNING : no 'TREE_SIMPLIFY' defined in 'DEFAULT' section of " + \
                           self.argDict[ "settings" ] + "...running with TREE_SIMPLIFY==False." )
        logging.debug( "  PROV TREE : using TREE_SIMPLIFY = " + str( TREE_SIMPLIFY ) )

        if TREE_SIMPLIFY and self.is_interesting( d ) :
          self.descendant_meta.append( d )
        else :
          self.descendant_meta.append( d )


  ####################
  #  IS INTERESTING  #
  ####################
  def is_interesting( self, d ) :
    if d[ "treeType" ] == "fact" and not d[ "node_name" ] == "clock" :
      return False
    else :
      return True


  #################
  #  CONTAINS OP  #
  #################
  # check if the input goal attribute
  # contains an aggregate operator.
  def contains_op( self, gatt ) :
    for op in self.ops :
      if op in gatt :
        return True
    return False


  #################
  #  CONTAINS OP  #
  #################
  # check if the input goal attribute
  # contains an aggregate function.
  def contains_agg( self, gatt ) :
    for agg in self.aggs :
      if agg in gatt :
        return True
    return False


  ############
  #  GET OP  #
  ############
  # grab the operation from the goal attribute string
  def get_op( self, gatt ) :
    if "+" in gatt :
      return "+"
    elif "-" in gatt :
      return "-"
    elif "*" in gatt :
      return "*"
    elif "/" in gatt :
      return "/"
    else :
      return "NO_OP"


  #############
  #  GET LHS  #
  #############
  # grab the lhs from the goal attribute string
  def get_lhs( self, gatt ) :
    for i in range( 0, len( gatt ) ) :
      if gatt[ i ] in self.ops :
        return gatt[ i+1 : ]
    return gatt


  ####################
  #  GET CLEAN GATT  #
  ####################
  # grab the goal attribute
  # remove aggs
  # remove operators
  def get_clean_gatt( self, gatt ) :

    logging.debug( "  GET CLEAN GATT : gatt = " + gatt )

    # remove aggs
    for agg in self.aggs :
      if gatt.startswith( agg ) and ">" in gatt :
        gatt = gatt.replace( agg, "" )
        gatt = gatt.replace( ">", "" )

    # remove operators
    for i in range( 0, len( gatt ) ) :
      if gatt[ i ] in self.ops :
        return gatt[ : i ]

    logging.debug( "GET CLEAN GATT : returning gatt = " + gatt )
    return gatt


  ####################################
  #  GET TRIGGER RECORD FOR SUBGOAL  #
  ####################################
  # use the map between goal attributes and record data
  # to generate the trigger record for the subgoal
  def get_trigger_record_for_subgoal( self, gatt_to_data, satt_list ) :

    satt_list = [ satt[ 1 ] for satt in satt_list ] # remove attIDs

    logging.debug( "  GET TRIGGER RECORD FOR SUBGOAL : gatt_to_data = " + str( gatt_to_data ) )
    logging.debug( "  GET TRIGGER RECORD FOR SUBGOAL : satt_list    = " + str( satt_list ) )

    triggerRecord = []

    for satt in satt_list :

      logging.debug( "  GET TRIGGER RECORD FOR SUBGOAL : satt = " + str( satt ) )

      # keep wildcards
      if satt == "_" :
        triggerRecord.append( satt )

      # keep fixed integer data
      elif satt.isdigit() :
        triggerRecord.append( satt )

      # keep fixed string data
      elif ( satt.startswith( "'" ) and satt.endswith( "'" ) ) or \
           ( satt.startswith( '"' ) and satt.endswith( '"' ) ) :
        triggerRecord.append( satt )

      else :
        triggerRecord.append( gatt_to_data[ satt ] )

    logging.debug( "  GET TRIGGER RECORD FOR SUBGOAL : triggerRecord = " + str( triggerRecord ) )

    return triggerRecord


  ########################
  #  CHECK SUBGOAL TYPE  #
  ########################
  def check_subgoal_type( self, subgoalName ) :

    logging.debug( "  CHECK SUBGOAL TYPE : subgoalName = " + subgoalName )

    self.cursor.execute( "SELECT fid FROM Fact WHERE name=='" + subgoalName + "'" )
    fid_list = self.cursor.fetchall()
    fid_list = tools.toAscii_list( fid_list )

    # clock, next_clock, and crash are edbs only
    if subgoalName == "clock" or \
       subgoalName == "next_clock" or \
       subgoalName == "crash" :

      return [ True, False ]

    else :
      if len( fid_list ) > 0 :
        is_edb = True
      else :
        is_edb = False

      self.cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + subgoalName + "'" )
      rid_list = self.cursor.fetchall()
      rid_list = tools.toAscii_list( rid_list )

      if len( rid_list ) > 0 :
        is_idb = True
      else :
        is_idb = False

      return [ is_edb, is_idb ]


#########
#  EOF  #
#########
