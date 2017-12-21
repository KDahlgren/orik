#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, sys

import DerivTree, RuleNode, FactNode, provTools

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools
from Node import Node

# **************************************** #

class GoalNode( Node ) :

  #####################
  #  SPECIAL ATTRIBS  #
  #####################
  descendants = []
  name        = None
  isNeg       = None
  seedRecord  = None
  results     = []

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, isNeg, seedRecord, results, cursor ) :

    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )
    logging.debug( "in GoalNode.GoalNode : " + name )
    logging.debug( "name       = " + name )
    logging.debug( "isNeg      = " + str( isNeg ) )
    logging.debug( "seedRecord = " + str( seedRecord ) )
    logging.debug( ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" )

    self.name       = name
    self.isNeg      = isNeg
    self.seedRecord = seedRecord
    self.results    = results

    # ///////////////////////////////////////////////////////// #
    # NODE CONSTRUCTOR: treeType, name, isNeg, record, program results, dbcursor
    Node.__init__( self, "goal", name, isNeg, seedRecord, results, cursor )

    # ***************************************************************** #
    # ***************************************************************** #
    #                      HANDLE CLOCK GOALS
    #
    if self.name == "clock" :

      logging.debug( "  GOAL NODE : hit a clock" )

      triggerRecordList = self.getClockTriggerRecordList()

    # ***************************************************************** #
    # ***************************************************************** #
    #                      HANDLE NON-CLOCK GOALS
    #
    elif self.isFactOnly( ) :

      logging.debug( "  GOAL NODE : hit a non-clock edb" )

      triggerRecordList = [ seedRecord ]

    else :

      logging.debug( "  GOAL NODE : hit an idb" )

      # ///////////////////////////////////////////////////////// #
      # get all id pairs ( original rid, provenance rid ) 
      # for this name

      allIDPairs = self.getAllIDPairs()

      logging.debug( "  GOAL NODE : allIDPairs = " + str( allIDPairs ) )

      # ///////////////////////////////////////////////////////// #
      # for each original rid, map original goal atts to values
      # from the seed record.

      oridList  = [ aPair[0] for aPair in allIDPairs ]
      ogattMaps = self.getGoalAttMaps( oridList )

      logging.debug( "  GOAL NODE : oridList  = " + str( oridList ) )
      logging.debug( "  GOAL NODE : ogattMaps = " + str( ogattMaps ) )

      # ///////////////////////////////////////////////////////// #
      # for each provenance rule id, use the corresponding orid map
      # for goal atts to seed record values to map provenance rule 
      # goal atts to seed record values or None.
      # Map WILDCARDs to None.

      pgattMaps = self.mergeMaps( allIDPairs, ogattMaps )

      logging.debug( "  GOAL NODE : pgattMaps = " + str( pgattMaps ) )

      # ///////////////////////////////////////////////////////// #
      # for each prid, grabs the full set of records from 
      # the provenance relation which may have triggered 
      # the appearance of the seed record in the original 
      # rule relation.

      triggerRecordList = self.getAllTriggerRecords( pgattMaps )

    # ***************************************************************** #
    # ***************************************************************** #

    # ///////////////////////////////////////////////////////// #
    # set the descendants of this goal node.
    #
    # Need to make sure descendants list is empty or else
    # pyDot creates WAAAAAAAAY too many edges for some reason??? <.<

    logging.debug( "  GOAL NODE : triggerRecordList = " + str( triggerRecordList ) )

    self.descendants = []
    self.setDescendants( triggerRecordList )


  #############
  #  __STR__  #
  #############
  # the string representation of a GoalNode
  def __str__( self ) :
    if self.isNeg :
      negStr = "_NOT_"
      return "goal->" + negStr + " " + self.name + "(" + str(self.record) + ")"
    else :
      return "goal->" + self.name + "(" + str(self.record) + ")"


  ##################
  #  IS FACT ONLY  #
  ##################
  # check if the name of the goal node references a fact only
  def isFactOnly( self ) :

    # check fact relation
    self.cursor.execute( "SELECT fid FROM Fact WHERE name=='" + self.name + "'" )
    fid = self.cursor.fetchone()

    # check rule relation
    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + self.name + "'" )
    rid = self.cursor.fetchone()

    # CASE : rule is both a fact and a rule
    if fid and rid :
      return False

    # CASE : relation is fact only
    elif fid :
      return True

    # CASE : relation is rule only
    else :
      return False


  ###################
  #  GET CLOCK MAP  #
  ###################
  def getClockTriggerRecordList( self ) :

    # sanity check
    # all clock records adhere to the same arity-4 schema: src, dest, SndTime, DelivTime
    if not len(self.record) == 4 :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : clock record does not adhere to clock schema(src,dest,SndTime,DelivTime) : \nself.record = " + str(self.record) )

    # get clock record data
    src       = self.record[0]
    dest      = self.record[1]
    sndTime   = self.record[2]
    delivTime = self.record[3]

    # get all matching (or partially matching, in the case of '_') clock records
    # optimistic by default
    qSRC           = "src=='" + src + "'"
    qDEST          = " AND dest=='" + dest + "'"
    qSNDTIME       = " AND sndTime==" + sndTime + ""
    qDELIVTIME     = " AND delivTime==" + delivTime + ""
    qInclusionBool = " AND simInclude=='True'"

    # erase query components as necessary
    if "_" in src :
      qSRC = ""
    if "_" in dest :
      qDEST = ""
    if "_" in sndTime :
      qSNDTIME = ""
    if "_" in delivTime :
      qDELIVTIME = ""

    # handle empty SRC
    if qSRC == "" and not qDEST == "" :
      qDEST = qDEST.replace( "AND", "" )
    elif qSRC == "" and qDEST == "" and not qSNDTIME == "" :
      qSNDTIME = qSNDTIME.replace( "AND", "" )
    elif qSRC == "" and qDEST == "" and qSNDTIME == "" and not qDELIVTIME == "" :
      qDELIVTIME = qDELIVTIME.replace( "AND", "" )
    elif qSRC == "" and qDEST == "" and qSNDTIME == "" and qDELIVTIME == "" and not qInclusionBool == "" :
      qInclusionBool = qInclusionBool.replace( "AND", "" )

    # set query
    query = "SELECT src,dest,sndTime,delivTime FROM Clock WHERE " + qSRC + qDEST + qSNDTIME + qDELIVTIME + qInclusionBool

    logging.debug( "query = " + str(query) )

    # execute query
    self.cursor.execute( query )
    triggerRecordList = self.cursor.fetchall()
    triggerRecordList = tools.toAscii_multiList( triggerRecordList )

    return triggerRecordList


  ######################
  #  GET ALL ID PAIRS  #
  ######################
  # match the ids of oiginal rules to the ids of the associated derived provenance rules.
  # there exists only one prov rule per original rule.
  # return a list of binary lists connecting original rule ids and 
  # corresponding provenance rule ids.

  def getAllIDPairs( self ) :

    logging.debug( "  GET ALL ID PAIRS : running process..." )

    # ---------------------------------------------------------- #
    #                      ORIG RULE DATA                        #
    # ---------------------------------------------------------- #
    # get all original rule ids associated with the name
    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + self.name + "'" )
    origIDs = self.cursor.fetchall()
    origIDs = tools.toAscii_list( origIDs )

    # get the complete attList and subgoalList associated with each original rule
    # store as arrays in an array [ rid, [attList], [subgoalList] ]
    origInfo = []
    for orid in origIDs :

      # get attList
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid='" + orid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      # get subgoalList
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid='" + orid + "'" )
      subgoalList = self.cursor.fetchall()
      subgoalList = tools.toAscii_multiList( subgoalList )

      origInfo.append( [ orid, attList, subgoalList ] )

    logging.debug( "  GET ALL ID PAIRS : origInfo = " + str( origInfo ) )

    # ---------------------------------------------------------- #
    #                      PROV RULE DATA                        #
    # ---------------------------------------------------------- #
    # get all provenance rule ids associated with the name
    # first, get all rule id, rule name pairs

    self.cursor.execute( "SELECT rid,goalName FROM Rule" )
    idNamePairs = self.cursor.fetchall()
    idNamePairs = tools.toAscii_multiList( idNamePairs )

    # next, collect the rids of goalnames starting with self.name+"_prov"
    provIDs = []
    for idName in idNamePairs :
      currID   = idName[0]
      currName = idName[1]
      if currName.startswith( self.name + "_prov" ) :
        provIDs.append( currID )

    logging.debug( "  GET ALL ID PAIRS : provIDs = " + str( provIDs ) )

    # get the complete attList and subgoalList associated with each original rule
    # store as arrays in an array [ rid, [attList], [subgoalList] ]
    provInfo = []
    for prid in provIDs :
      # get attList
      self.cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid='" + prid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      # get subgoalList
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid='" + prid + "'" )
      subgoalList = self.cursor.fetchall()
      subgoalList = tools.toAscii_multiList( subgoalList )

      provInfo.append( [ prid, attList, subgoalList ] )

    logging.debug( "  GET ALL ID PAIRS : provInfo = " + str( provInfo ) )

    # ---------------------------------------------------------- #
    #                         MATCH                              #
    # ---------------------------------------------------------- #
    # match original rids with provenance rids by matching
    # attLists and subgoals.

    idPairs = []
    for origIDInfo in origInfo :
      orid     = origIDInfo[0]
      oAttList = origIDInfo[1]
      oSubList = origIDInfo[2]

      for provIDInfo in provInfo :
        prid     = provIDInfo[0]
        pAttList = provIDInfo[1]
        pSubList = provIDInfo[2]

        if self.checkListEquality( oAttList, pAttList ) and self.checkListEquality( oSubList, pSubList ) :
          idPairs.append( [ orid, prid ] ) # save pair

    logging.debug( "  GET ALL ID PAIRS : idPairs = " + str( idPairs ) )

    return idPairs


  #########################
  #  CHECK LIST EQUALITY  #
  #########################
  # check list equality
  # 1. list lengths must be equal
  # 2. all elements in each list must appear in the other list

  def checkListEquality( self, list1, list2 ) :

    logging.debug( "  CHECK LIST EQUALITY : running process..." )
    logging.debug( "  CHECK LIST EQUALITY : list1 = " + str( list1 ) )
    logging.debug( "  CHECK LIST EQUALITY : list2 = " + str( list2 ) )

    flag = True

    # check length equality
    if not len( list1 ) == len( list2 ) :
      flag = False

    # check contents equality
    for item in list1 :
      if not item in list2 :
        flag = False
        break
  
    logging.debug( "  CHECK LIST EQUALITY : returning " + str( flag ) )
    return flag


  #######################
  #  GET GOAL ATT MAPS  #
  #######################
  # return an ordered array of binary arrays connecting goal 
  # attributes from the original rule the values from the seed record.
  def getGoalAttMaps( self, oridList ) :
    ogattMap = []

    # get the ordered list of goal attributes for each orid
    oridAttLists = []
    for orid in oridList :
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + orid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )
      attList = [ aPair[1] for aPair in attList ]

      oridAttLists.append( [ orid, attList ] )

    # for each orid:attList, connect atts to vals from seed record
    for oridInfo in oridAttLists :
      thisorid    = oridInfo[0]
      thisattList = oridInfo[1]

      # sanity check
      # the number of goal atts in the original rule must match
      # the number of values in the seed record.
      if (len( thisattList ) < len( self.record )) or (len( thisattList ) > len( self.record )) :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : number of attributes in goal attribute list for " + self.name + " does not match the number of values in the seed record:\nattribute list = " + str(thisattList) + "\nrecord = " + str(self.record) )

      # map atts to values from the seed record
      thisAttValList = []
      for i in range(0,len(thisattList)) :
        att = thisattList[ i ]
        val = self.record[ i ]
        thisAttValList.append( [ att, val ] )

      ogattMap.append( [ thisorid, thisAttValList ] )

    return ogattMap


  ################
  #  MERGE MAPS  #
  ################
  # for each provenance rule id, use the corresponding orid map
  # for goal atts to seed record values to map provenance rule 
  # goal atts to seed record values or None.
  # Map WILDCARDs to None.
  def mergeMaps( self, allIDPairs, ogattMaps ) :
    pgattMaps = []

    # get list of all prids
    pridList = [ aPair[1] for aPair in allIDPairs ]

    for prid in pridList :

      # get the goal att list for this provenance rule
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + prid + "'" )
      pgattList = self.cursor.fetchall()
      pgattList = tools.toAscii_multiList( pgattList )
      pgattList = [ arr[1] for arr in pgattList ]

      # get corresponding original rule id
      orid = self.getORID( prid, allIDPairs )

      # ///////////////////////////////////////////////////////// #
      # get map of goal atts for the original rule 
      # to seed record values.
      # ------------------------------------------------------------- #
      # Transform into dictionary for convenience
      thisogattMap = self.getOGattMap( orid, ogattMaps )

      ogattDict = {}
      for arr in thisogattMap :
        att = arr[0]
        val = arr[1]

        # sanity check
        if att in ogattDict.keys() and not val == ogattDict[ att ] :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : multiple data values exist for the same attribute.\nattribute = " + att + "\nval = " + val + " and ogattDict[ att ] = " + ogattDict[ att ] )
        else : # add to dictionary
          ogattDict[ att ] = val
      # ------------------------------------------------------------- #

      # map provenance goal atts to values from the seed record based on 
      # the attribute mappings in the original rule.
      # unspecified atts are mapped to None.
      # WILDCARDs are mapped to None.
      pattMapping = []
      for patt in pgattList :
        #if patt == "__WILDCARD__" :
        if patt == "_" :
          pattMapping.append( [ patt, None ] )
        elif patt in ogattDict.keys() :
          pattMapping.append( [ patt, ogattDict[ patt ] ] )
        else :
          pattMapping.append( [ patt, None ] )

      pgattMaps.append( [ prid, pattMapping ] )
      # ///////////////////////////////////////////////////////// #

    return pgattMaps


  ################################################
  #  GET O(riginal Rule) G(oal) ATT(ribute) MAP  #
  ################################################
  def getOGattMap( self, orid, ogattMaps ) :

    for aMap in ogattMaps :
      currorid = aMap[0]
      currmap  = aMap[1]

      if orid == currorid :
        return currmap

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : the original rule id " + orid + " has no goal attribute mapping in ogattMaps = " + str(ogattMaps) )


  ##############
  #  GET ORID  #
  ##############
  def getORID( self, prid, allIDPairs ) :

    for aPair in allIDPairs :
      currorid = aPair[0]
      currprid = aPair[1]

      if prid == currprid :
        return currorid

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : provenance id " + prid + " has no corresponding original rule id. You got major probs... =["  )


  #############################
  #  GET ALL TRIGGER RECORDS  #
  #############################
  # return list of binary lists connecting each prid
  # with a list of records (stored as lists) from the 
  # provenance record which may have triggered the
  # appearance of the seed record in the original rule
  # relation.

  def getAllTriggerRecords( self, pgattMaps ) :

    logging.debug( "  GET ALL TRIGGER RECORDS : pgattMaps = " + str( pgattMaps ) )

    pTrigRecs = []

    for attMap in pgattMaps :
      prid    = attMap[0]
      mapping = attMap [1]

      # get full relation name
      self.cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + prid + "'" )
      pname = self.cursor.fetchone() # goalName should be unique per provenance rule
      pname = tools.toAscii_str( pname )

      # get full results table
      resultsTable = self.results[ pname ]

      # get list of valid records which agree with the provenance rule 
      # goal attribute mapping
      # correctness relies upon ordered nature of the mappings.
      validRecList = []
      for rec in resultsTable :

        if self.checkAgreement( mapping, rec ) :
          validRecList.append( rec )

      pTrigRecs.append( [ prid, mapping, validRecList ] )

    return pTrigRecs


  #####################
  #  CHECK AGREEMENT  #
  #####################
  def checkAgreement( self, mapping, rec ) :

    # sanity check
    if not len(mapping) == len( rec ) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : arity of provenance schema not equal to arity of provenance records:\nmapping = " + str(mapping) + "\nrec = " + str(rec) + "\nYou got probs. =[ Aborting..." )

    for i in range(0,len(mapping)) :
      attValPair = mapping[i]
      att        = attValPair[0]
      val        = attValPair[1]
      recval     = rec[i]

      if val == None :
        pass
      elif val == "_" :
        pass
      elif val == recval :
        pass
      else :
        return False

    return True


  #####################
  #  SET DESCENDANTS  #
  #####################
  # goal nodes may have more than one descendant in the case of wildcards
  # and when multiple firing records exist for the particular.
  def setDescendants( self, triggerRecordList ) :

    logging.debug( "  SET DESCENDANTS : running process..." )

    # ==================================================== #
    # ==================================================== #
    #   CASE goal is a fact node
    if tools.isFact( self.name, self.cursor ) :

      # ************************************************* #
      #                HANDLE CLOCK FACTS                 #
      #
      # triggerRecordList := list of trigger records 

      if self.name == "clock" :

        logging.debug( "  SET DESCENDANTS : hit a clock" )

        # spawn a fact for each trigger record
        for rec in triggerRecordList :
          self.spawnFact( rec )

      # ************************************************* #
      #                HANDLE OTHER FACTS                 #
      #
      # triggerRecordList := list of trigger records 

      elif self.isFactOnly() :

        logging.debug( "  SET DESCENDANTS : hit a non-clock edb" )

        # spawn a fact for each trigger record
        for rec in triggerRecordList :
          self.spawnFact( rec )

      # ************************************************* #
      #                HANDLE OTHER FACTS                 #
      #               ALSO DEFINED BY RULES               #
      #
      # triggerRecordList := list of trinary lists 
      #     containing the prid, the prov att map, and
      #     the list of trigger records.

      else :

        logging.debug( "  SET DESCENDANTS : hit an edb/idb" )

        # get complete list of trigger records
        trigList = []
        for trigRec in triggerRecordList :
          provID     = trigRec[0]
          provAttMap = trigRec[1]
          recList    = trigRec[2]

          # for empty record lists, use node record.
          if recList == [] :
            trigList.extend( [ self.record ] )

          # otherwise, spawn fact nodes to all records
          else :
            trigList.extend( trigRec[2] )

        # spawn a fact for each trigger record
        for rec in trigList :
          self.spawnFact( rec )

    # ==================================================== #
    #   CASE goal is a rule

    else :

      logging.debug( ">>> self.name = " + str( self.name ) )
      logging.debug( ">>> self.isNeg = " + str( self.isNeg ) )
      logging.debug( ">>> self.seedRecord = " + str( self.seedRecord ) )
      logging.debug( ">> triggerRecordList : " + str( triggerRecordList ) )

      for trigRec in triggerRecordList :
        provID     = trigRec[0]
        provAttMap = trigRec[1]
        recList    = trigRec[2]

        # spawn a rule for each valid record
        for rec in recList :
          self.spawnRule( provID, provAttMap, rec )

    # ==================================================== #
    # ==================================================== #


  ################
  #  SPAWN FACT  #
  ################
  def spawnFact( self, trigRec ) :

    # check if trig rec has wildcards. if so, collect all valid records aligning with the wildcards.
    recList = []
    for d in trigRec :
      if d == "_" :
        recList = self.getRecsFromWildcardRec( trigRec )

    if recList == [] :
      logging.debug( "spawning fact with trigFac '" + str( trigRec ) + "'" )
      self.descendants.append( DerivTree.DerivTree( self.name, None, "fact", self.isNeg, None, trigRec, self.results, self.cursor ) )

    else :
      for rec in recList :
        logging.debug( "spawning fact with rec '" + str( rec ) + "'" )
        self.descendants.append( DerivTree.DerivTree( self.name, None, "fact", self.isNeg, None, rec, self.results, self.cursor ) )


  ################################
  #  GET RECS FROM WILDCARD REC  #
  ################################
  # given record containing wildcards
  # return list of records aligning with the wildcard record
  def getRecsFromWildcardRec( self, trigRec ) :

    targetRelation = self.results[ self.name ]

    recList = [] # list of records aligning with the trig rec containing wildcards

    for tup in targetRelation :
      validRec = True
      for i in range(0,len(tup)) :
        if tup[i] == trigRec[i] or trigRec[i] == "_" :
          continue
        else :
          validRec = False

      if validRec :
        recList.append( tup )
      else :
        continue

    return recList


  ################
  #  SPAWN RULE  #
  ################
  def spawnRule( self, rid, provAttMap, seedRecord ) :

    self.descendants.append( DerivTree.DerivTree( self.name, rid, "rule", False, provAttMap, seedRecord, self.results, self.cursor ) )


#########
#  EOF  #
#########
