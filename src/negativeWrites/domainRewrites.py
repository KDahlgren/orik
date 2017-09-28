#/usr/bin/env python

'''
domainRewrites.py
'''

import inspect, os, string, sys
import sympy

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

if not os.path.abspath( __file__ + "/../../dedt/translators" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../dedt/translators" ) )

from dedt        import Rule
from evaluators  import c4_evaluator
from translators import c4_translator
from utils       import clockTools, tools, dumpers

# ------------------------------------------------------ #


#####################
#  DOMAIN REWRITES  #
#####################
def domainRewrites( parentRID, sidInParent, posName, posNameRIDs, newDMRIDList, COUNTER, cursor ) :

  print "&&& posName : " + posName

  # ---------------------------------------------- #
  # get parent name                                #
  # ---------------------------------------------- #
  cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + parentRID + "'" )
  parentName = cursor.fetchone()
  parentName = tools.toAscii_str( parentName )

  # ---------------------------------------------- #
  # buid new domain rule name                      #
  # ---------------------------------------------- #
  domainRuleName = "dom_not_" + posName + "_from_" + parentName

  # ---------------------------------------------- #
  # add new rule for the domain subgoal            #
  # ---------------------------------------------- #
  newRuleMeta = addDomainRules( parentRID, sidInParent, parentName, posName, domainRuleName, posNameRIDs, newDMRIDList, cursor )

  # ---------------------------------------------- #
  # add domain idb subgoal to each new DM rule     #
  # ---------------------------------------------- #
  addSubgoalsToRules( domainRuleName, newDMRIDList, cursor )

  return newRuleMeta


#####################
#  ADD DOMAIN EDBS  #
#####################
# add the results for the original program evaluation 
# as edb facts in the newly rewritten program.
# the result facts inform negative write domain subgoal
# ranges.
def addDomainEDBs( original_prog, cursor ) :

  # --------------------------------------------------- #
  # run original program and grab results dictionary    #
  # --------------------------------------------------- #

  results_array = c4_evaluator.runC4_wrapper( original_prog )
  parsedResults = tools.getEvalResults_dict_c4( results_array )

  # --------------------------------------------------- #
  # save results as edb facts in IR db                  #
  # --------------------------------------------------- #

  for relationName in parsedResults :

    print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
    print "relationName : " + relationName

    # build fact name
    newEDBName = "dom_" + relationName + "_evalres"

    print "newEDBName : " + newEDBName

    # ---------------------------------------------------------- # 
    # no evaluation data exists for this relation
    if parsedResults[ relationName ] == [] :

      # set fact info
      fid      = tools.getID()
      timeArg += 1
      print ">>> INSERT INTO Fact VALUES ('" + fid + "','" + newEDBName + "','" + str( timeArg ) + "')"
      cursor.execute( "INSERT INTO Fact VALUES ('" + fid + "','" + newEDBName + "','" + str( timeArg ) + "')" )

      # get fact schema
      # observe a relation defined in a dedalust program  can only be empty in this context if it is an IDB
      # because c4 define statements are derived from relations defined in the dedalus program only.
      cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + relationName + "'" )
      ridList   = cursor.fetchall()
      ridList   = tools.toAscii_list( ridList )
      pickedRID = ridList[0]

      cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + pickedRID + "'" )
      attData = cursor.fetchall()
      attData = tools.toAscii_multiList( attData )

      # set fact data
      fattID = 0
      for att in attData :

        attID   = att[0]
        attName = att[1]
        attType = att[2]

        if attType == "string" :
          d = '"___DEFAULTSTR___"'
        else :
          d = 9999999999

        print ">>> INSERT INTO FactAtt (" + fid + "," + str( fattID ) + "," + str( d ) + "," + attType + ")"
        cursor.execute( "INSERT INTO FactAtt VALUES ('" + fid + "','" + str( fattID ) + "','" + str( d ) + "','" + str( attType ) + "')" )

        fattID += 1

      #tools.bp( __name__, inspect.stack()[0][3], "blah" )

    # ---------------------------------------------------------- # 
    # evaluation data exists for this relation
    else :
      for dataTup in parsedResults[ relationName ] :

        # build fact id
        fid = tools.getID()

        # default time arg to 1. domain edb facts are true starting at time 1.
        timeArg = 1

        # set fact info
        print ">>> INSERT INTO Fact VALUES ('" + fid + "','" + newEDBName + "','" + str( timeArg ) + "')"
        cursor.execute( "INSERT INTO Fact VALUES ('" + fid + "','" + newEDBName + "','" + str( timeArg ) + "')" )

        fattID = 0
        for d in dataTup :

          # get data type for d
          if d.isdigit() :
            attType = "int"
          else :
            attType = "string"

          # modify string data with quotes
          if attType == "string" :
            d = '"' + d + '"'

          # set fact data
          print ">>> INSERT INTO FactAtt (" + fid + "," + str(fattID) + "," + str( d ) + "," + attType + ")"
          cursor.execute( "INSERT INTO FactAtt VALUES ('" + fid + "','" + str(fattID) + "','" + str( d ) + "','" + str( attType ) + "')" )

          fattID += 1

  #tools.dumpAndTerm( cursor )


######################
#  ADD DOMAIN RULES  #
######################
# add one rule informing the domains of the goal attributes for the indicated not_ rule
def addDomainRules( parentRID, sidInParent, parentName, posName, domainRuleName, posNameRIDs, newDMRIDList, cursor ) :

  # ---------------------------------------------- #
  # generate a new rid for this rule.              #
  # ---------------------------------------------- #

  rid = tools.getID()

  # ---------------------------------------------- #
  # get goal name                                  #
  # ---------------------------------------------- #

  goalName = domainRuleName

  # ---------------------------------------------- #
  # build and save all goal data                   #
  # ---------------------------------------------- #

  randomDMRID = newDMRIDList[0]
  univAttData = setGoal( rid, goalName, randomDMRID, newDMRIDList, cursor )

  # -------------------------------------------------- #
  # collect all universal subgoals for the domain rule #
  # -------------------------------------------------- #
  # return a array

  univSubgoals = collectUniversalBoundSubgoals( randomDMRID, parentRID, sidInParent, posName, parentName, univAttData, cursor )

  # ---------------------------------------------------- #
  # collect all existential subgoals for the domain rule #
  # ---------------------------------------------------- #
  # return a array

  exisSubgoals = collectExistentialBoundSubgoals( univSubgoals, posNameRIDs, cursor )

  #if goalName.startswith( "dom_not_node_from_not_log_from_missing_log" ) :
  #  for sub in exisSubgoals :
  #    print sub
  #  tools.bp( __name__, inspect.stack()[0][3], "shit" )

  # ---------------------------------------------------- #
  # save all subgoals                                    #
  # ---------------------------------------------------- #

  saveAllSubgoals( rid, univSubgoals, exisSubgoals, cursor )

  # ---------------------------------------------- #
  # generate new rule meta objects to pass         #
  # to provenance rewriter.                        #
  # ---------------------------------------------- #

  return Rule.Rule( rid, cursor )


##############
#  SET GOAL  #
##############
# build and save the goal information for the new domain rule.
# rid          := the rid for the new domain rule
# goalName     := the goal name for the new domain rule
# randomDMRID  := one of the rids for the not_ rule set built via the negaive writes process
# newDMRIDList := the complete list of rids for the new not_ rules
def setGoal( rid, goalName, randomDMRID, newDMRIDList, cursor ) :

  # --------------------------------- #
  # set defaults                      #
  # --------------------------------- #
  goalTimeArg = ""
  rewritten   = True

  # --------------------------------- #
  # save goal info                    #
  # --------------------------------- #
  cursor.execute("INSERT INTO Rule VALUES ('" + rid + "','" + goalName + "','" + goalTimeArg + "','" + str(rewritten) + "')")

  # --------------------------------- #
  # collect all universal atts        #
  # --------------------------------- #
  # the set of existential attributes in the domain rule is exactly the 
  # set of goal attributes for the not_ DM rules.
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + randomDMRID + "'" )
  univAttData = cursor.fetchall()
  univAttData = tools.toAscii_multiList( univAttData )

  # ----------------------------------- #
  # collect all existential atts        #
  # ----------------------------------- #
  # iterate over all new not_ rules and collect all variables per rule
  # not appearing in the list of goal attributes.

  goalAttList = [ x[1] for x in univAttData ]
  exisAttList = [] # collect previously appended existential att names here to avoid duplicates
  exisAttData = []
  for dmrid in newDMRIDList :

    allSubgoalAtts = []

    # get all sids for this rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid=='" + dmrid + "'" )
    sidList = cursor.fetchall()
    sidList = tools.toAscii_list( sidList )

    for sid in sidList :
      # get all subgoal att data
      cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + dmrid + "' AND sid=='" + sid + "'" )
      subgoalAttData = cursor.fetchall()
      subgoalAttData = tools.toAscii_multiList( subgoalAttData )

      for att in subgoalAttData :
        # grab all existential atts
        attName = att[1]

        # existential atts do not exist in the goal attribute list
        # do not duplicate existential atts in the collection structure
        # wildcards are not existential atts
        if not attName in goalAttList and not attName in exisAttList and not attName == "_" :
          exisAttData.append( att )
          exisAttList.append( attName )

  # ----------------------------------- #
  # save goal attributes                #
  # ----------------------------------- #
  allAttData = univAttData + exisAttData
  for att in allAttData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]

    print "INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(attID) + "','" + attName + "','" + attType + "')"
    cursor.execute( "INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(attID) + "','" + attName + "','" + attType + "')" )


  return univAttData


######################################
#  COLLECT UNIVERSAL BOUND SUBGOALS  #
######################################
# randomDMRID := one of the rids in the set of new not_ rules for the targeted negated subgoal
#                observe the goal schema for "not_thing" rules is identical to the goal schema
#                for "thing" rules.
# parentRID   := the rid for the parent rule negating the targeted subgoal
# sidINParent := the sid of the targeted negated subgoal in the parent rule
# posName     := the positive name of the targeted negated subgoal
# parentName  := the name of the parent rule negating the targeted subgoal
# cursor      := the IR db pointer
def collectUniversalBoundSubgoals( randomDMRID, parentRID, sidInParent, posName, parentName, univAttData, cursor ) :

  print 
  print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
  print "BUILDING UNIVERSAL BOUND SUBGOALS"
  print "randomDMRID rule : " + dumpers.reconstructRule( randomDMRID, cursor )
  print "parentRID rule   : " + dumpers.reconstructRule( parentRID, cursor )
  print "sidInParent      : " + sidInParent
  print "posName          : " + posName
  print "parentName       : " + parentName

  universalBoundSubgoals = []

  # ===================================================================== #
  # ===================================================================== #

  # ----------------------------------- #
  # build parent dom subgoal            #
  # ----------------------------------- #
  parentSubgoalName = "dom_" + parentName + "_evalres"

  print "parentSubgoalName : " + parentSubgoalName

  # ---------------------------------------------- #
  # get parent rule attribute list                 #
  # ---------------------------------------------- #
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + parentRID + "'" )
  parentGoalAttList = cursor.fetchall()
  parentGoalAttList = tools.toAscii_multiList( parentGoalAttList )

  # ---------------------------------------------- #
  # get negated subgoal attribute list from parent #
  # ---------------------------------------------- #
  cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + parentRID + "' AND sid=='" + sidInParent + "'" )
  subAttDataInParent = cursor.fetchall()
  subAttDataInParent = tools.toAscii_multiList( subAttDataInParent )

  # --------------------------------------------------------------- #
  # map parent goal att indexes to subgoal att indexes or wildcards #
  # --------------------------------------------------------------- #
  parentSubgoalAttIndexMap = {}
  for paratt in parentGoalAttList :
    pattID     = paratt[0]
    pattName   = paratt[1]
    subIndexes = []
    for subatt in subAttDataInParent :
      sattID   = subatt[0]
      sattName = subatt[1]
      if pattName == sattName :
        subIndexes.append( sattID )
    parentSubgoalAttIndexMap[ pattID ] = subIndexes

  # ------------------------------------------------------------------------------------------------------ #
  # map parent subgoal att vars to the corresponding att vars in the uniform attribute set for the DM rule #
  # ------------------------------------------------------------------------------------------------------ #
  # get uniform attribute list
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + randomDMRID + "'" )
  uniformAttList = cursor.fetchall()
  uniformAttList = tools.toAscii_multiList( uniformAttList )

  # populate map
  subToUniformMap = {}
  for i in range(0,len(subAttDataInParent)) :
    subatt     = subAttDataInParent[i]
    subAttName = subatt[1]

    subToUniformMap[ subAttName ] = uniformAttList[i]

  # ---------------------------------------------------------------------------------- #
  # map parent goal att vars to vars from the uniform att list for the negated subgoal #
  # ---------------------------------------------------------------------------------- #
  parentSubgoalAttMap = {}
  for parAttIndex in parentSubgoalAttIndexMap :
    correspondingSubAttIndexList = parentSubgoalAttIndexMap[ parAttIndex ]

    # this attribute in the parent goal does not appear in the negated subgoal att list.
    # use a wildcard.
    if correspondingSubAttIndexList == [] :
      parAttType = parentGoalAttList[ parAttIndex ][2]
      parentSubgoalAttMap[ parAttIndex ] = [ parAttIndex, "_", parAttType ]

    # this attribute in the parent goal appears in the negated subgoal att list.
    # replace with the corresponding uniform attribute variable for the subgoal rewrite.
    else :
      for subAttIndex in correspondingSubAttIndexList :
        parentRuleSubAttVar = subAttDataInParent[ subAttIndex ][1]
        uniformVar          = subToUniformMap[ parentRuleSubAttVar ]
      parentSubgoalAttMap[ parAttIndex ] = uniformVar # should be identical across subgoal indexes

  # -------------------- #
  # build parent subgoal #
  # -------------------- #
  # save subgoal contents in a dictionary
  parentSubgoal                     = {}
  parentSubgoal[ "sid" ]            = tools.getID()
  parentSubgoal[ "subgoalName" ]    = parentSubgoalName
  parentSubgoal[ "subgoalTimeArg" ] = "" # default
  parentSubgoal[ "subgoalAttDict" ] = parentSubgoalAttMap
  parentSubgoal[ "argName" ]        = ""

  # ============================================================== #
  # ============================================================== #

  # ----------------------------------- #
  # build original dom subgoal          #
  # ----------------------------------- #
  negatedPositiveSubgoalName = "dom_" + posName + "_evalres"

  # ----------------------------------------------- #
  # map parent subgoal att vars to uniform att vars #
  # ----------------------------------------------- #
  # correctness depends upon the schemas of the positive and not_
  # definitions of the targeted negated subgoal to be identical.
  # this can only be guaranteed after the uniformity rewrite.
  negatedPositiveSubgoalAttMap = {}
  for att in subAttDataInParent :
    attID   = att[0]
    attName = att[1]
    if attName == "_" :
      attType = uniformAttList[ attID ][2]
      negatedPositiveSubgoalAttMap[ attID ] = [ attID, "_", attType ]
    else :
      attName = uniformAttList[attID][1]
      attType = uniformAttList[attID][2]
      negatedPositiveSubgoalAttMap[ attID ] = [ attID, attName, attType ]

  # ------------------------------ #
  # build negated positive subgoal #
  # ------------------------------ #
  negatedPositiveSubgoal                     = {}
  negatedPositiveSubgoal[ "sid" ]            = tools.getID()
  negatedPositiveSubgoal[ "subgoalName" ]    = negatedPositiveSubgoalName
  negatedPositiveSubgoal[ "subgoalTimeArg" ] = "" # default
  negatedPositiveSubgoal[ "subgoalAttDict" ] = negatedPositiveSubgoalAttMap
  negatedPositiveSubgoal[ "argName" ]        = "notin" # negated positive

  # ============================================================== #
  # ============================================================== #

  # ----------------------------------- #
  # build original dom subgoal          #
  # ----------------------------------- #
  positivePositiveSubgoalName = "dom_" + posName + "_evalres"

  # ----------------------------------------------- #
  # map parent subgoal att vars to uniform att vars #
  # ----------------------------------------------- #
  # correctness depends upon the schemas of the positive and not_
  # definitions of the targeted negated subgoal to be identical.
  # this can only be guaranteed after the uniformity rewrite.
  # 
  # the attributes in the positive domain subgoal for the targetted negated relation
  # are exactly the in the negated domain subgoal relation in this rule 
  # minus the attributes incoporated into the parent domain subgoal of this rule.

  parentEvalRes_atts_only = [ parentSubgoalAttMap[x][1] for x in parentSubgoalAttMap ]

  positivePositiveSubgoalAttMap = {}
  for att in univAttData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]
    if attName in parentEvalRes_atts_only :
      attName = "_"
    positivePositiveSubgoalAttMap[ attID ] = [ attID, attName, attType ]

  # ------------------------------ #
  # build negated positive subgoal #
  # ------------------------------ #
  positivePositiveSubgoal                     = {}
  positivePositiveSubgoal[ "sid" ]            = tools.getID()
  positivePositiveSubgoal[ "subgoalName" ]    = positivePositiveSubgoalName
  positivePositiveSubgoal[ "subgoalTimeArg" ] = "" # default
  positivePositiveSubgoal[ "subgoalAttDict" ] = positivePositiveSubgoalAttMap
  positivePositiveSubgoal[ "argName" ]        = "" # positive positive

  # ============================================================== #
  # ============================================================== #

  universalBoundSubgoals = []

  if not allWildcardAtts( parentSubgoal ) :
    universalBoundSubgoals.append( parentSubgoal )

  if not allWildcardAtts( negatedPositiveSubgoal ) :
    universalBoundSubgoals.append( negatedPositiveSubgoal )

  if not allWildcardAtts( positivePositiveSubgoal ) :
    universalBoundSubgoals.append( positivePositiveSubgoal )

  print "DONE BUILDING UNIVERSAL BOUND SUBGOALS"

  return universalBoundSubgoals


#######################
#  ALL WILDCARD ATTS  #
#######################
# given the dictionary representation of a subgoal
# return True if all subgoal atts are wildcards, false otherwise
def allWildcardAtts( subgoalDict ) :

  subgoalAttDict = subgoalDict[ "subgoalAttDict" ]

  for att in subgoalAttDict :

    attData = subgoalAttDict[ att ]
    attName = attData[1]

    if not attName == "_" :
      return False

  return True


########################################
#  COLLECT EXISTENTIAL BOUND SUBGOALS  #
########################################
def collectExistentialBoundSubgoals( universalBoundSubgoals, posNameRIDs, cursor ) :

  print
  print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
  print "BUILDING EXISTENTIAL BOUND SUBGOALS"
  print "universalBoundSubgoals : "
  for sub in universalBoundSubgoals :
    print sub
  print "posNameRIDs :"
  for r in posNameRIDs :
    print dumpers.reconstructRule( r, cursor )

  existentialBoundSubgoals = []

  # -------------------------- #
  # extract all universal vars #
  # -------------------------- #
  univars = []
  for subgoalDict in universalBoundSubgoals :
    subgoalAttDict = subgoalDict[ "subgoalAttDict" ]

    for subindex in subgoalAttDict :
      attData = subgoalAttDict[ subindex ]
      attVar  = attData[1]
      if not attVar in univars and not attVar == "_" :
        univars.append( attVar )

  # ---------------------------------------------------------------------------------------- #
  # collect all subgoals from pos rules with all universal variables replaced with wildcards #
  # ---------------------------------------------------------------------------------------- #
  for posrid in posNameRIDs :

    print "<><> posNameRIDs rule : " + dumpers.reconstructRule( posrid, cursor )

    # get all sids
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid=='" + posrid + "'" )
    sidList = cursor.fetchall()
    sidList = tools.toAscii_list( sidList )

    for possid in sidList :

      # ---------------- #
      # get subgoal name #
      # ---------------- #
      cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + posrid + "' AND sid=='" + possid + "'" )
      exisSubgoalName = cursor.fetchone()
      exisSubgoalName = tools.toAscii_str( exisSubgoalName )

      # ------------------------- #
      # get subgoal time argument #
      # ------------------------- #
      cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid=='" + posrid + "' AND sid=='" + possid + "'" )
      exisSubgoalTimeArg = cursor.fetchone()
      exisSubgoalTimearg = tools.toAscii_str( exisSubgoalTimeArg )
      if type( exisSubgoalTimeArg ) is tuple :
        exisSubgoalTimeArg = exisSubgoalTimeArg[0]

      # ------------------- #
      # get subgoal att map #
      # ------------------- #
      # ====================================== #
      # CASE : subgoal is an EDB               #
      # ====================================== #
      if tools.isFact_only( exisSubgoalName, cursor ) :

        if exisSubgoalName == "clock" :

          # just need to get the data for one clock fact
          cursor.execute( "SELECT src,dest,sndTime,delivTime FROM Clock" )
          fact = cursor.fetchall()
          fact = tools.toAscii_multiList( fact )
          fact = fact[0]

          factData = {}
          attID = 0
          for d in fact :
            attName = d
            if type( d ) is int :
              attType = "int"
            elif d.isdigit() :
              attType = "int"
            else :
              attType = "string"
            factData[ attID ] = [ attID, attName, attType ]
            attID += 1

          #tools.bp( __name__, inspect.stack()[0][3], "factData : " + str( factData ) )

        else :
          # get an fid for this edb
          cursor.execute( "SELECT fid FROM Fact WHERE name=='" + exisSubgoalName + "'" )
          thisSubgoalEDBFID = cursor.fetchone()
          thisSubgoalEDBFID = tools.toAscii_str( thisSubgoalEDBFID )

          # get fact data
          cursor.execute( "SELECT attID,attName,attType FROM FactAtt WHERE fid=='" + thisSubgoalEDBFID + "'" )
          factData = cursor.fetchall()
          factData = tools.toAscii_multiList( factData )

        # get subgoal attribute data
        cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + posrid + "' AND sid=='" + possid+ "'" )
        subAttData = cursor.fetchall()
        subAttData = tools.toAscii_multiList( subAttData )

        # map subgoal attributes to att types from the corresponding fact schema
        attData = {}
        for i in range(0,len(factData)) :
          fact    = factData[i]
          subatt  = subAttData[i]

          attID   = fact[0]
          attName = subatt[1]
          attType = fact[2]

          attData[ attID ] = [ attID, attName, attType ]

      # ====================================== #
      # CASE : suboal is an IDB                #
      # ====================================== #
      else :

        # get original name
        orig_name = exisSubgoalName.split( "_from" )
        orig_name = orig_name[0] # remove stuff from _from and after
        if orig_name.startswith( "not_" ) :
          orig_name = orig_name[4:]
        print "orig_name = " + str( orig_name )

        # get an rid for this idb
        #cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + exisSubgoalName + "'" )
        cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + orig_name + "'" )
        thisSubgoalIDBRID = cursor.fetchone()
        thisSubgoalIDBRID = tools.toAscii_str( thisSubgoalIDBRID )

        # get att data from IDB definition
        cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + thisSubgoalIDBRID + "'" )
        orig_subgoalAttList = cursor.fetchall()
        orig_subgoalAttList = tools.toAscii_multiList( orig_subgoalAttList )

        # get att data from subgoal from positive rule
        cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + posrid + "' AND sid=='" + possid + "'" )
        subgoal_subgoalAttList = cursor.fetchall()
        subgoal_subgoalAttList = tools.toAscii_multiList( subgoal_subgoalAttList )

        attData = {}
        for i in range(0,len(orig_subgoalAttList)) :
          orig_att         = orig_subgoalAttList[i]
          sub_att          = subgoal_subgoalAttList[i]

          attID            = orig_att[0]
          attName          = sub_att[1]
          attType          = orig_att[2]
          
          attData[ attID ] = [ attID, attName, attType ]

      print "attData : " + str( attData )

      exisSubgoalAttMap = {}
      for attID in attData :
        att     = attData[ attID ]
        attID   = att[0]
        attName = att[1]
        attType = att[2]

        if attName in univars and not attName == "_" :
          attName = "_"

        exisSubgoalAttMap[ attID ] = [ attID, attName, attType ]

      # ------------------- #
      # get subgoal add arg #
      # ------------------- #
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid=='" + posrid + "' AND sid=='" + possid + "'" )
      exisAddArg = cursor.fetchone()
      if exisAddArg :
        exisAddArg = tools.toAscii_str( exisAddArg )
      else :
        exisAddArg = ""

      # ------------------------------ #
      # build negated positive subgoal #
      # ------------------------------ #
      exisSubgoal                     = {}
      exisSubgoal[ "sid" ]            = tools.getID()
      exisSubgoal[ "subgoalName" ]    = exisSubgoalName
      exisSubgoal[ "subgoalTimeArg" ] = exisSubgoalTimeArg
      exisSubgoal[ "subgoalAttDict" ] = exisSubgoalAttMap
      exisSubgoal[ "argName" ]        = exisAddArg

      existentialBoundSubgoals.append( exisSubgoal )

  print "DONE BUILDING EXISTENTIAL BOUND SUBGOALS"

  return existentialBoundSubgoals


#######################
#  SAVE ALL SUBGOALS  #
#######################
# rid          := the rid for the new domain rule for the targeted subgoal
# univSubgoals := the array of universal subgoals
# exisSubgoals := the array of existential subgoals
# cursor       := the IR db cursor
def saveAllSubgoals( rid, univSubgoals, exisSubgoals, cursor ) :

  # ========================================================== #
  # ========================================================== #

  # ----------------------- #
  # save universal subgoals #
  # ----------------------- #
  for sub in univSubgoals :
    sid            = sub[ "sid" ]
    subgoalName    = sub[ "subgoalName" ] 
    subgoalTimeArg = sub[ "subgoalTimeArg" ]
    subgoalAttDict = sub[ "subgoalAttDict" ]
    argName        = sub[ "argName" ]

    # ---------------- #
    # save to Subgoals #
    # ---------------- #
    print "INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')"
    cursor.execute( "INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')" )

    # ------------------ #
    # save to SubgoalAtt #
    # ------------------ #
    for subatt in subgoalAttDict :

      attID   = subatt
      attName = subgoalAttDict[ subatt ][1] 
      attType = subgoalAttDict[ subatt ][2] 
      print "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "','" + attType + "')"
      cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "','" + attType + "')" )

    # ---------------------- #
    # save to SubgoalAddArgs #
    # ---------------------- #
    print "INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + argName + "')"
    cursor.execute( "INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + argName + "')" )

  # ========================================================== #
  # ========================================================== #

  # ------------------------- #
  # save existential subgoals #
  # ------------------------- #
  for sub in exisSubgoals :
    sid            = sub[ "sid" ]
    subgoalName    = sub[ "subgoalName" ]
    subgoalTimeArg = sub[ "subgoalTimeArg" ]
    subgoalAttDict = sub[ "subgoalAttDict" ]
    argName        = sub[ "argName" ]

    tmp = []
    for s in subgoalAttDict :
      subattData = subgoalAttDict[ s ]
      tmp.append( subattData[ 1 ] )

    flag = False
    for attName in tmp :
      if not attName == "_" :
        flag = True

    # skip subgoal if atts are only wildcards
    if not flag :
      continue

    else :
      # ---------------- #
      # save to Subgoals #
      # ---------------- #
      print "INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')"
      cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")

      # ------------------ #
      # save to SubgoalAtt #
      # ------------------ #
      for subatt in subgoalAttDict :

        attID   = subatt
        attName = subgoalAttDict[ subatt ][1]
        attType = subgoalAttDict[ subatt ][2]
        print "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "','" + attType + "')"
        cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str(attID) + "','" + attName + "','" + attType + "')" )

      # ---------------------- #
      # save to SubgoalAddArgs #
      # ---------------------- #
      print "INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + argName + "')"
      cursor.execute( "INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + argName + "')" )


  #print dumpers.reconstructRule( rid, cursor )
  #tools.bp( __name__, inspect.stack()[0][3], "blee" )


###########################
#  ADD SUBGOALS TO RULES  #
###########################
# add domain subgoals to new demorgan's rules.
# dom_not_posName( [goalAttList] ) <= these are idbs.
# write in idb rules next.
# write in edb facts informing the domain idb rules afterwrd.
#
# subName      := the dom_not_whatever goal name
# newDMRIDList := the list of rids for the new not_whatever rules
# cursor       := pointer to cursor
#
def addSubgoalsToRules( domainRuleName, newDMRIDList, cursor ) :

  # -------------------------------------------- #
  # get goal att list for the dom_not_whatever 
  # rule previously written in addDomainRules
  # -------------------------------------------- #

  # get rid for the domain rule
  cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + domainRuleName + "'" )
  rid = cursor.fetchone()
  if not rid or rid == "" :
    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : writing domain subgoals, but no '" + domainRuleName + "' rule exists. aborting..." )
  else :
    rid = tools.toAscii_str( rid )

  # get the goal attribute list for the domain rule
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + rid + "'" )
  goalAttList = cursor.fetchall()
  goalAttList = tools.toAscii_multiList( goalAttList )


  for rid in newDMRIDList :

    # ----------------------------------- #
    # generate sid                        #
    # ----------------------------------- #
    sid = tools.getID()

    # ----------------------------------- #
    # fixed subgoal time arg to nothing   #
    # ----------------------------------- #
    subgoalTimeArg = ""

    # ----------------------------------- #
    # insert subgoal metadata             #
    # ----------------------------------- #
    cursor.execute( "INSERT INTO Subgoals VALUES ('" + rid + "','"  + sid + "','" + domainRuleName + "','" + subgoalTimeArg +"')" )

    # ----------------------------------- #
    # insert subgoal att data             #
    # ----------------------------------- #

    attID = 0
    for att in goalAttList :

      attName = att[1]
      attType = att[2]

      cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

      attID += 1


#########
#  EOF  #
#########
