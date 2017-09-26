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
def domainRewrites( parentRID, posName, newDMRIDList, cursor ) :

  # ---------------------------------------------- #
  # get parent name                                #
  # ---------------------------------------------- #
  cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + parentRID + "'" )
  parentName = cursor.fetchone()
  parentName = tools.toAscii_str( parentName )

  # ---------------------------------------------- #
  # buid new subgoal name                          #
  # ---------------------------------------------- #
  subName = "dom_not_" + posName + "_from_" + parentName

  # ---------------------------------------------- #
  # add domain idb subgoal to each new DM rule     #
  # ---------------------------------------------- #
  addSubgoalsToRules( subName, newDMRIDList, cursor )

  # ---------------------------------------------- #
  # add new rule for the domain subgoal            #
  # ---------------------------------------------- #
  newRuleMeta = addDomainRules( parentRID, posName, subName, newDMRIDList, cursor )

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

    # build fact name
    newEDBName = "dom_" + relationName + "_evalres"

    for dataTup in parsedResults[ relationName ] :

      # build fact id
      fid = tools.getID()

      # default time arg to 1. domain edb facts are true starting at time 1.
      timeArg = 1

      # set fact info
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


######################
#  ADD DOMAIN RULES  #
######################
# add one rule informing the domains of the goal attributes 
# of the not_ version of the positive rule.
# e.g. dom_not_thing( A0, A1, A2 ) :- dom_posName( A2, A1, _  ), notin dom_thing( A0,A1,A2 )
def addDomainRules( parentRID, posName, subName, newDMRIDList, cursor ) :

  # ---------------------------------------------- #
  # generate a new rid for this rule.              #
  # ---------------------------------------------- #

  rid = tools.getID()

  # ---------------------------------------------- #
  # get goal name                                  #
  # ---------------------------------------------- #

  goalName = subName

  # ---------------------------------------------- #
  # get goal atts                                  #
  # ---------------------------------------------- #
  # pick an rid from the set of new DM rules
  # valid because schema for domain subgoal 
  # is identical across DM rules.
  randomRID = newDMRIDList[0]

  print dumpers.reconstructRule( randomRID, cursor )

  # get all attribute data
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + randomRID + "'" )
  attData = cursor.fetchall()
  attData = tools.toAscii_multiList( attData )

  #if goalName == "dom_not_log_from_missing_log" :
  #  print
  #  print "/////////"
  #  print attData
  #  #tools.bp( __name__, inspect.stack()[0][3], "blah" )


  # ---------------------------------------------- #
  # set goal                                       #
  # ---------------------------------------------- #

  # set goal info
  timeArg       = "" # default
  rewrittenFlag = False # default
  cursor.execute("INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + rid + "','" + goalName + "','" + timeArg + "','" + str(rewrittenFlag) + "')")

  # set goal attributes
  for att in attData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]

    print ">>>>> INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(attID) + "','" + attName + "','" + attType + "')"
    cursor.execute( "INSERT INTO GoalAtt VALUES ('" + rid + "','" + str(attID) + "','" + attName + "','" + attType + "')" )


  #if goalName == "dom_not_log_from_missing_log" :
  #  tools.bp( __name__, inspect.stack()[0][3], "blah" )

  # ---------------------------------------------- #
  # set parent edb subgoal                         #
  # ---------------------------------------------- #

  # get parent name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + parentRID + "'"  )
  parentName = cursor.fetchone()
  parentName = tools.toAscii_str( parentName )

  subName = "dom_" + parentName + "_evalres"

  # generate subgoal id
  sid = tools.getID()

  # map parent attributes to negated subgoal attributes and types
  # parent att index -> [ subgoal att index, attribute type (derived from parent definition) ]
  parAttMap = getGoalToSubgoalAttMap( parentRID, randomRID, cursor )

  # map the new rule att indexes to att variables
  indexNameMap = goalIndexToAttNameMap( attData )

  # build the list of attributes for the parent subgoal
  parSubAttData = []
  for parAtt in parAttMap :
    parIndex     = parAtt
    data         = parAttMap[ parIndex ]
    subIndexList = data[0]
    dataType     = data[1]

    # just need one of the matching subgoal att indexes
    chosenIndex = None
    for ind in subIndexList :
      if not ind < 0 :
        chosenIndex = ind
        break

    attID   = parIndex

    if chosenIndex :
      attName = indexNameMap[ chosenIndex ]
    else :
      attName = "_"

    attType = dataType

    parSubAttData.append( [ attID, attName, attType ] )

  # set subgoal info
  subgoalTimeArg = "" # default
  cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subName + "','" + subgoalTimeArg + "')")

  # set subgoal attributes
  for att in parSubAttData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]
    cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')")

  # set subgoal add args
  addArg = "" # default
  cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")


  # ---------------------------------------------- #
  # set pos rule version subgoal                   #
  # ---------------------------------------------- #
  # the attributes of the subgoal are the 
  # attributes of the goal.

  # build subgoal name
  posSubName = "dom_" + posName + "_evalres"

  # generate subgoal id
  sid = tools.getID()

  # subgoalTimeArg default to nothing
  subgoalTimeArg = ""

  # set subgoal info
  cursor.execute("INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + posSubName + "','" + subgoalTimeArg + "')")

  # set subgoal attributes
  for att in attData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]
    cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')")

  # set subgoal add args
  addArg = "notin" # default
  cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + addArg + "')")

  # ---------------------------------------------- #
  # generate new rule meta objects to pass         #
  # to provenance rewriter.                        #
  # ---------------------------------------------- #

  return Rule.Rule( rid, cursor )


################################
#  GOAL INDEX TO ATT NAME MAP  #
################################
def goalIndexToAttNameMap( attData ) :

  indexNameMap = {}

  for att in attData :
    attID = att[0]
    attName = att[1]
    attType = att[2]

    indexNameMap[ attID ] = attName

  return indexNameMap


#################################
#  GET GOAL TO SUBGOAL ATT MAP  #
#################################
# key   := parent index
# value := corresponding subgoal
def getGoalToSubgoalAttMap( parentRID, randomRID, cursor ) :

  # get parent goal attributes list
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + parentRID + "'" )
  pattData = cursor.fetchall()
  pattData = tools.toAscii_multiList( pattData )

  pattList = [ x[1] for x in pattData ]
  pattType = [ x[2] for x in pattData ]

  # get name of negated subgoal
  cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + randomRID + "'" )
  subgoalName = cursor.fetchone()
  subgoalName = tools.toAscii_str( subgoalName )

  # get subgoal id
  # only supports one instance of same negated subgoal per rule.
  # TODO : generalize to N instances of the same subgoal.
  cursor.execute( "SELECT sid FROM Subgoals WHERE subgoalName=='" + subgoalName + "'" )
  sid = cursor.fetchall()
  sid = tools.toAscii_list( sid )
  sid = sid[0]

  # get subgoal att list
  cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + parentRID + "' AND sid=='" + sid + "'" )
  sattData = cursor.fetchall()
  sattData = tools.toAscii_multiList( sattData )

  sattList = [ x[1] for x in sattData ]

  parAttMap = {}
  for i in range(0,len(pattList)) :

    patt     = pattList[i]
    pattType = pattList [i]
    pindex = i

    sindexList = []
    for j in range(0,len(sattList)) :

      satt = sattList[j]

      if j < len(sattList) and patt == satt :
        sindexList.append( j )
       
      # parent attribute does not appear at this index.
      # if parent attribute does not appear in this subgoal,
      # then the key will point to an empty list.
      else :
        sindexList.append( -1 )

    parAttMap[ pindex ] = [ sindexList, pattType ]

  return parAttMap


###########################
#  ADD SUBGOALS TO RULES  #
###########################
# add domain subgoals to new demorgan's rules.
# dom_not_posName( [goalAttList] ) <= these are idbs.
# write in idb rules next.
# write in edb facts informing the domain idb rules afterwrd.
def addSubgoalsToRules( subName, newDMRIDList, cursor ) :

  for rid in newDMRIDList :

    # ----------------------------------- #
    # get goal att list
    cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + rid + "'" )
    goalAttList = cursor.fetchall()
    goalAttList = tools.toAscii_multiList( goalAttList )

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
    cursor.execute( "INSERT INTO Subgoals VALUES ('" + rid + "','"  + sid + "','" + subName + "','" + subgoalTimeArg +"')" )

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
