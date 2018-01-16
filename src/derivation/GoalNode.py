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
  def __init__( self, name="DEFAULT", isNeg=None, record=[], parsedResults={}, cursor=None ) :

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

    # dictionary of metadata for node descendants.
    # { prov_rid : { 'goalName'    : <string>,
    #                'triggerData' : <array of strings/ints> }, ... }
    self.descendant_meta = {} # make sure this is empty

    logging.debug( "  descendant_meta = " + str( self.descendant_meta ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    # -------------------------------- #
    # make sure record exists in the 
    # eval results for this relation

    if not self.name == "FinalState"                 and \
       not self.name == "__KD__TESTNODE__KD__"       and \
       not "_" in self.record                        and \
       not self.record in parsedResults[ self.name ] and \
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

    logging.debug( "  GENERATE DESCENDANT META : prov_rid_to_valid_records = " + str( prov_rid_to_valid_records ) )

    # -------------------------------- #
    # generate the descendant metadata
    # prov_rid : { goalName    : <string>,
    #              triggerData : <array of strings/ints> }

    for pdata in prov_rid_and_name_list :

      prov_rid                     = pdata[ 0 ]
      goalName                     = pdata[ 1 ]
      triggerData                  = prov_rid_to_valid_records[ prov_rid ]
      self.descendant_meta[ prov_rid ] = { 'goalName' : goalName, 'triggerData' : triggerData }

    logging.debug( "  GENERATE DESCENDANT META : self.descendant_meta = " + str( self.descendant_meta ) )


  ################################
  #  GET PROV RID AND NAME LIST  #
  ################################
  # get the list of rid(s) for rules defining this relation
  # capable of generating the input record.
  # breaks if user inputs relations with '_prov' in the name.
  def get_prov_rid_and_name_list( self ) :

    self.cursor.execute( "SELECT rid,goalName FROM Rule WHERE goalName LIKE '" + self.name + "%_prov%'" )
    prov_rid_and_name_list = self.cursor.fetchall()
    prov_rid_and_name_list = tools.toAscii_multiList( prov_rid_and_name_list )

    # all rules must have corresponding provenance rules
    if not len( prov_rid_and_name_list ) > 0 and not self.name == "__TestNode__" :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : no provenance rule for '" + self.name + "'" )

    return prov_rid_and_name_list


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

    valid_prov_records = []

    for prov_record in self.parsedResults[ pname ] :

      logging.debug( "  GET PROV RECORDS : prov_record = " + str( prov_record ) )

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
