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

class GoalNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################

  treeType    = "goal"


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name="DEFAULT", isNeg=None, record=[], parsedResults={}, cursor=None, prev_prov_recs={} ) :

    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )
    logging.debug( "in GoalNode.GoalNode : " + name )
    logging.debug( "  name            = " + name )
    logging.debug( "  isNeg           = " + str( isNeg ) )
    logging.debug( "  record          = " + str( record ) )

    self.name            = name
    self.isNeg           = isNeg
    self.record          = record
    self.parsedResults   = parsedResults
    self.cursor          = cursor
    self.prev_prov_recs  = prev_prov_recs
    logging.debug( "  prev_prov_recs = " + str( self.prev_prov_recs ) )
    logging.debug( "  ->len(prev_prov_recs) = " + str( len( self.prev_prov_recs ) ) )

    # dictionary of metadata for node descendants.
    # { prov_rid : { 'goalName'    : <string>,
    #                'triggerData' : <array of strings/ints> }, ... }
    self.descendant_meta = {} # make sure this is empty

    logging.debug( "  descendant_meta = " + str( self.descendant_meta ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    # -------------------------------- #
    # make sure record exists in the 
    # eval results for this relation

    if not self.name == "FinalState"           and \
       not self.name == "__KD__TESTNODE__KD__" and \
       not "_" in self.record                  and \
       not self.in_results()                   and \
       self.isNeg == False :

      tools.bp( __name__, inspect.stack()[0][3], \
                "  GOAL CONSTRUCTOR : FATAL ERROR : record '" + str( record ) + "'" + \
                " does not appear in the results for relation '" + self.name + \
                "' :\n" + str( self.parsedResults[ self.name ] ) )

    # -------------------------------- #
    # initialize node object

    Node.__init__( self, treeType = self.treeType, \
                         name     = self.name, \
                         isNeg    = self.isNeg, \
                         record   = self.record, \
                         results  = self.parsedResults, \
                         cursor   = self.cursor )

    # -------------------------------- #
    # generate descendant metadata

    if not self.name == "FinalState" and \
       not self.name == "__KD__TESTNODE__KD__" :
      self.generate_descendant_meta()


  ################
  #  IN RESULTS  #
  ################
  # check if the record exists in the parsed results.
  def in_results( self ) :

    for res in self.parsedResults[ self.name ] :
      if self.is_match( res ) :
        return True

    return False


  ##############
  #  IS MATCH  #
  ##############
  # check if the input result tuple 'matches' any tuple in the evaluation results
  # for this relation.
  def is_match( self, res ) :

    for i in range( 0, len( self.record ) ) :

      res_datum    = res[ i ]
      record_datum = self.record[ i ]

      # remove any quotes
      if record_datum.startswith( "'" ) and record_datum.endswith( "'" ) :
        record_datum = record_datum.replace( "'", "" )
      elif record_datum.startswith( '"' ) and record_datum.endswith( '"' ) :
        record_datum = record_datum.replace( '"', "" )

      if record_datum == "_" :
        pass

      else :
        if not res_datum == record_datum :
          return False

    return True


  #############
  #  __STR__  #
  #############
  # the string representation of a GoalNode
  def __str__( self ) :

    if self.isNeg :
      negStr = "_NOT_"
      return "goal->" + negStr + self.name + "(" + str(self.record) + ")"

    else :
      return "goal->" + self.name + "(" + str(self.record) + ")"


  ##############################
  #  GENERATE DESCENDANT META  #
  ##############################
  # generate the meta data required to spawn the desendant rule nodes.
  def generate_descendant_meta( self ) :

    # -------------------------------- #
    # get the rid(s) for the prov rule(s) 

    prov_rid_and_name_list = self.get_prov_rid_and_name_list()
    logging.debug( "  GENERATE DESCENDANT META : prov_rid_and_name_list = " + str( prov_rid_and_name_list ) )

    # -------------------------------- #
    # generate the list of
    # corresponding records from
    # the provenance relations for this
    # rule per provenance relation
    # for this rule

    prov_rid_to_valid_records = {} # maps prov rule rids to arrays

    for pdata in prov_rid_and_name_list :

      prid                              = pdata[0]
      pname                             = pdata[1]
      valid_records                     = self.get_valid_prov_records( pname )
      prov_rid_to_valid_records[ prid ] = valid_records

    logging.debug( ">>>name="  + self.name + "," + str( self.record ) )
    logging.debug( "  GENERATE DESCENDANT META : prov_rid_to_valid_records = " + str( prov_rid_to_valid_records ) )

#    # -------------------------------- #
#    # remove duplicates
#
#    tmp  = {}
#    tmp2 = {}
#    for sid in sid_to_name_and_polarity :
#      tmp[ str( sid_to_name_and_polarity[ sid ] ) ] = sid
#    for subgoalInfo in tmp :
#      array_str = subgoalInfo.translate( None, string.whitespace )
#      array_str = array_str.replace( "[", "" )
#      array_str = array_str.replace( "]", "" )
#      array_str = array_str.replace( "'", "" )
#      tmp2[ tmp[ subgoalInfo ] ] = array_str.split( "," )
#
#    sid_to_name_and_polarity = copy.copy( tmp2 )
#    logging.debug( "  GENERATE DESCENDANT META : sid_to_name_and_polarity (after de-pulication) = " + str( sid_to_name_and_polarity ) )

    # -------------------------------- #
    # generate the descendant metadata
    # prov_rid : { goalName    : <string>,
    #              triggerData : <array of strings/ints> }

    for pdata in prov_rid_and_name_list :

      prov_rid                         = pdata[ 0 ]
      goalName                         = pdata[ 1 ]
      triggerData                      = prov_rid_to_valid_records[ prov_rid ]
      self.descendant_meta[ prov_rid ] = { 'goalName' : goalName, 'triggerData' : triggerData }

    logging.debug( "  GENERATE DESCENDANT META : self.descendant_meta = " + str( self.descendant_meta ) )


  ################################
  #  GET PROV RID AND NAME LIST  #
  ################################
  # get the list of rid(s) for rules defining this relation
  # capable of generating the input record.
  # this code will _NOT_ if the user inputs relations ending with '_prov' or '_vars'.
  def get_prov_rid_and_name_list( self ) :

    logging.debug( "  GET PROV RID AND NAME LIST : checking self.name = " + self.name )

    # the provenance rule for any _vars rule is the _vars rule.
    if self.name.endswith( "_vars" ) :
      self.cursor.execute( "SELECT rid,goalName FROM Rule WHERE goalName LIKE '" + self.name + "'" )
      rid_and_name_list = self.cursor.fetchall()
      rid_and_name_list = tools.toAscii_multiList( rid_and_name_list )

    else :
      # get any associated _prov rules
      self.cursor.execute( "SELECT rid,goalName FROM Rule WHERE goalName LIKE '" + self.name + "_prov%'" )
      rid_and_name_list = self.cursor.fetchall()
      rid_and_name_list = tools.toAscii_multiList( rid_and_name_list )

    logging.debug( "  GET PROV RID AND NAME LIST : rid_and_name_list = " + str( rid_and_name_list ) )

    # all rules must have corresponding provenance rules
    if not len( rid_and_name_list ) > 0 and not self.name == "__TestNode__" :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : no provenance rules for '" + self.name + "'" )

    return rid_and_name_list


  ############################
  #  GET VALID PROV RECORDS  #
  ############################
  # get list of provenance records matching the 
  # input record
  # a record matches a prov_record if the first 
  # n components of each tuple are identical,
  # where n is the number of components in the record tuple.
  def get_valid_prov_records( self, pname ) :

    logging.debug( "  GET VALID PROV RECORDS : running process... " )
    logging.debug( "  GET VALID PROV RECORDS : pname       = " + pname )
    logging.debug( "  GET VALID PROV RECORDS : self.record = " + str( self.record ) )
    logging.debug( "  GET VALID PROV RECORDS : self.prev_prov_recs = " + str( self.prev_prov_recs ) )

    valid_prov_records = []

    for prov_record in self.parsedResults[ pname ] :

      #logging.debug( "  GET VALID PROV RECORDS : prov_record = " + str( prov_record ) )

      if not pname in self.prev_prov_recs or ( not prov_record in self.prev_prov_recs[ pname ] ) :

        # CASE : the original record contains wildcards
        if "_" in self.record :
          flag = True
          for i in range( 0, len( self.record ) ) :
            if self.record[ i ] == "_" :
              pass
            else :
              if not prov_record[ i ] == self.record[ i ] :
                flag = False

          if flag :
            valid_prov_records.append( prov_record )

        # CASE : ther original record contains no wildcards
        else :
          if prov_record[ : len( self.record ) ] == self.record :
            valid_prov_records.append( prov_record )

    return valid_prov_records


#########
#  EOF  #
#########
