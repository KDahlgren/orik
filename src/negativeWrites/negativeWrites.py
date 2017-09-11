#/usr/bin/env python

'''
negativeWrites.py
   Define the functionality for collecting the provenance of negative subgoals.
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

import deMorgans
import rewriteNegativeEDBs

# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
NEGATIVEWRITES_DEBUG = tools.getConfig( "DEDT", "NEGATIVEWRITES_DEBUG", bool )

arithOps = [ "+", "-", "*", "/" ]


#####################
#  NEGATIVE WRITES  #
#####################
def negativeWrites( EOT, cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running negative writes ..."

  newRuleMeta = setNegativeRules( EOT, [], 0, cursor )

  # dump to test
  if NEGATIVEWRITES_DEBUG :
    print
    print "<><><><><><><><><><><><><><><><><><>"
    print ">>> DUMPING FROM negativeWrites <<<"
    print "<><><><><><><><><><><><><><><><><><>"
    dumpers.programDump(  cursor )

  return newRuleMeta


########################
#  SET NEGATIVE RULES  #
########################
# the DB instance accessible via 'cursor' is the input program P
# translated into the intermediate representation amenable to
# syntactical anaylsis and/or translation into a particular flavor
# of Datalog.
#
# use the input program to build another program P' incorporating
# negative writes.
# 
# if P' contains negated IDB subgoals, repeat negativeWrites on P'.
#
def setNegativeRules( EOT, oldRuleMeta, COUNTER, cursor ) :

  print "COUNTER = " + str( COUNTER )

  if NEGATIVEWRITES_DEBUG :
    print " ... running set negative rules ..."

  # --------------------------------------------------- #
  # run input program and collect results               #
  # --------------------------------------------------- #
  #print "made it here1."

  # get results from running the input program P
  pResults = evaluate( COUNTER, cursor )

  #print "made it here2."

  # --------------------------------------------------- #
  # rewrite lines containing negated IDBs               #
  # --------------------------------------------------- #
  # maintian list of IDB goal names to rewrite.
  # IDBs pulled from rules across the entire program.
  negatedList = []

  newDMRIDList = []

  pRIDs = getAllRuleRIDs( cursor )

  for rid in pRIDs :

    if ruleContainsNegatedIDB( rid, cursor ) :
      negatedIDBNames = rewriteParentRule( rid, cursor )
      negatedList.extend( negatedIDBNames )

      # ....................................... #
      # remove duplicates
      #tmp0  = []
      #tmp1  = []
      #names = [ x[0] for x in negatedList ]
      #sids  = [ x[1] for x in negatedList ]
      #print "names = "  + str( names )
      #print "sids  = "  + str( sids  )
      #for i in range(0,len(names)) :
      #  name = names[i]
      #  if not name in tmp1 :
      #    tmp0.append( [ name, sids[i]] ) 
      #negatedList = tmp0
      # ....................................... #

    else :
      pass

  # --------------------------------------------------- #
  # add new rules for negated IDBs                      #
  # --------------------------------------------------- #

  #if COUNTER == 1 :
  #  print negatedList
  #  tools.bp( __name__, inspect.stack()[0][3], "COUNTER = " + str( COUNTER ) )

  #####################################################################
  # NOTE :                                                            #
  # negatedList is an array of [ IDB goalName, parent rule id ] pairs #
  #####################################################################
  DMList   = []
  newRules = oldRuleMeta
  for nameData in negatedList :

    posName   = nameData[0]  # name of negated IDB subgoal
    parentRID = nameData[1]  # rid of parent rule

    # ............................................................... #
    # collect all rids for this IDB name
    posNameRIDs = getRIDsFromName( posName, cursor )

    # ............................................................... #
    # rewrite original rules to shift function calls in goal atts 
    # and rewrite as a series of new rules.
    # branch condition : 
    # shift arith ops if IDB defined by multiple rules
    # otherwise, just shift the equation from the goal to the body.
    newArithRuleRIDList = shiftArithOps( posNameRIDs, cursor )

    # build rule meta for provenance rewriter
    for rid in newArithRuleRIDList :
      newRule = Rule.Rule( rid, cursor )
      newRules.append( newRule )

    # ............................................................... #
    # rewrite original rules with uniform universal attribute variables
    # if relation possesses more than one IDB rule definition.
    if len( posNameRIDs ) > 1 :
      setUniformUniversalAttributes( posNameRIDs, cursor )

    # ............................................................... #
    # apply the demorgan's rewriting scheme to the rule set.
    newDMRIDList = applyDeMorgans( parentRID, posNameRIDs, cursor )
    DMList.append( [ newDMRIDList, posName ] )

    # build rule meta for provenance rewriter
    for rid in newDMRIDList :
      newRule = Rule.Rule( rid, cursor )
      newRules.append( newRule )

    # ............................................................... #
    # add domain subgoals.
    addDomainSubgoals( parentRID, posName, posNameRIDs, newDMRIDList, pResults, cursor )

    # --------------------------------------------------- #
    # replace existential vars with wildcards.            #
    # --------------------------------------------------- #
    setWildcards( EOT, newDMRIDList, cursor )

  # --------------------------------------------------- #
  # final checks
  # --------------------------------------------------- #
  # ................................................... #
  # resolve negated subgoals in the new demorgans       # 
  # rules.                                              #
  # ................................................... #
  filterDMNegations( DMList, cursor )

  #if COUNTER == 1 :
  #  tools.dumpAndTerm( cursor )

  # ................................................... #
  # rewrite rules with negated EDBs containing          #
  # wildcards                                           #
  # ................................................... #
  additionalNewRules = rewriteNegativeEDBs.rewriteNegativeEDBs( cursor )
  newRules.extend( additionalNewRules )

  if COUNTER == 1 :
    tools.dumpAndTerm( cursor )

  # ................................................... #
  # branch on continued presence of negated IDBs
  # ................................................... #
  # recurse if rewritten program still contains rogue negated IDBs
  if not newDMRIDList == [] and stillContainsNegatedIDBs( newDMRIDList, cursor ) :
    COUNTER += 1
    setNegativeRules( EOT, newRules, COUNTER, cursor )

  # otherwise, the program only has negated EDB subgoals.
  # get the hell out of here.
  return newRules


#########################
#  FILTER DM NEGATIONS  #
#########################
# examine all new rules generated as a result of the 
# de Morgan's rewrites.
# replace subgoals satisfying the characteristics of 
# circumstances triggering previous rewrites.
# replace double negatives with calls to the original 
# positive subgoals.
def filterDMNegations( DMList, cursor ) :

  print "DUMPING RULES HERE:"
  print "DMList = " + str( DMList )

  for ruleInfo in DMList :

    newRIDList = ruleInfo[0]
    origName   = ruleInfo[1]

    for rid in newRIDList :

      print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
      print "FILTERING RULE "
      print "old rule:"
      print dumpers.reconstructRule( rid, cursor )

      # ............................................... #
      # replace previously rewritten negated subgoals   #
      # ............................................... #
      replaceRewrittenSubgoals( rid, origName, cursor )

      # ............................................... #
      # resolve double negatives                        #
      # ............................................... #
      resolveDoubleNegatives( rid, origName, cursor )

      print "new rule:"
      print dumpers.reconstructRule( rid, cursor )

    #tools.dumpAndTerm( cursor )


##############################
#  RESOLVE DOUBLE NEGATIVES  #
##############################
def resolveDoubleNegatives( rid, fromName, cursor ) :

  # get all subgoal ids and names
  cursor.execute( "SELECT sid,subgoalName FROM Subgoals WHERE rid=='" + rid + "'" )
  subInfo = cursor.fetchall()
  subInfo = tools.toAscii_multiList( subInfo )

  print "subInfo = " + str( subInfo )

  # check for double negatives
  for sub in subInfo :

    sid  = sub[0]
    name = sub[1]

    if "not_" in name[0:4] and "_from_" in name :

      # check if negated
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
      sign = cursor.fetchone()
      sign = tools.toAscii_str( sign )

      if sign == "notin" :

        # build base name
        baseName = "_from_" + fromName

        # build positive name
        nameLen     = len( name )
        baseNameLen = len( baseName )
        posName     = name[ 4 : nameLen - baseNameLen ]

        # replace subgoal name with postivie equivalent.
        cursor.execute( "UPDATE Subgoals SET subgoalName=='" + posName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

        # remove negation
        cursor.execute( "UPDATE SubgoalAddArgs SET argName=='' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

        print "UPDATED DOUBLE NEGATIVE!"
        print dumpers.reconstructRule( rid, cursor )
        #tools.bp( __name__, inspect.stack()[0][3], "ici" )

################################
#  REPLACE REWRITTEN SUBGOALS  #
################################
# check if the rule at rid contains a subgoal 
# such that the not_ version of the subgoal 
# already exists as a result of a previous 
# DM rewrite.
# returns boolean
def replaceRewrittenSubgoals( rid, origName, cursor ) :

  print "... running negatesRewrittenSubgoal ..."
  print "origName : " + origName
  print "this rule : " + dumpers.reconstructRule( rid, cursor )

  # .............................................. #
  # generate negated name base                     #
  # (i.e. the "_from_" portion)                    #
  baseName = "_from_" + origName

  # .............................................. #
  # get sids for all negated subgoals in this rule
  cursor.execute( "SELECT sid From SubgoalAddArgs WHERE rid=='" + rid + "'" )
  sids = cursor.fetchall()
  sids = tools.toAscii_list( sids )

  # get subgoal names for negated subgoals
  negatedSubs = []
  for sid in sids :
    cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
    thisName = cursor.fetchone()
    thisName = tools.toAscii_str( thisName )
    negatedSubs.append( [ thisName, sid ] )

  # .............................................. #
  # get list of previously DM-rewritten rule names
  dmNames = prevDMRewrites_NamesOnly( cursor )

  print "dmNames : " + str( dmNames )

  # .............................................. #
  flag = False
  for sub in negatedSubs :

    name = sub[0]
    sid  = sub[1]

    # build hypothetical full name
    fullName = "not_" + name + baseName

    # check for existence
    if fullName in dmNames :

      # replace subgoal name
      cursor.execute( "UPDATE Subgoals SET subgoalName=='" + fullName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

      # replace negation argument
      cursor.execute( "UPDATE SubgoalAddArgs SET argName=='' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

      print "REPLACED REWRITTEN SUBGOAL!"


#################################
#  PREV DM REWRITES NAMES ONLY  #
#################################
def prevDMRewrites_NamesOnly( cursor ) :

  cursor.execute( "SELECT goalName FROM Rule WHERE ( goalName LIKE 'not_%' ) AND ( goalName LIKE '%_from_%' )" )
  goalNames = cursor.fetchall()
  goalNames = tools.toAscii_list( goalNames )

  # remove duplicates
  goalNames = set( goalNames )
  goalNames = list( goalNames )

  return goalNames


#################################
#  STILL CONTAINS NEGATED IDBS  #
#################################
# check if new rules contain negated IDBs
def stillContainsNegatedIDBs( newDMRIDList, cursor ) :

  flag = False

  for rid in newDMRIDList :
    if ruleContainsNegatedIDB( rid, cursor ) :
      flag = True
    else :
      continue

  return flag


###################
#  SET WILDCARDS  #
###################
def setWildcards( EOT, newDMRIDList, cursor ) :

  for rid in newDMRIDList :

    # ---------------------------------------- #
    # get goal att list
    cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + rid + "'" )
    goalAttList = cursor.fetchall()
    goalAttList = tools.toAscii_multiList( goalAttList )

    atts = [ x[1] for x in goalAttList ]

    # ---------------------------------------- #
    # get list of subgoal ids
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid=='" + rid + "'" )
    sids = cursor.fetchall()
    sids = tools.toAscii_list( sids )

    for sid in sids :

      # ---------------------------------------- #
      # branch on clock subgoals. 
      if isClock( rid, sid, cursor ) :
        handleClockSubgoals( EOT, rid, sid, cursor )

      else :
        handleNonClockSubgoals( atts, rid, sid, cursor )

      #handleNonClockSubgoals( atts, rid, sid, cursor )


###############################
#  HANDLE NON CLOCK SUBGOALS  #
###############################
def handleNonClockSubgoals( atts, rid, sid, cursor ) :
  # ---------------------------------------- #
  # get subgoal att list
  cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
  subgoalAttList = cursor.fetchall()
  subgoalAttList = tools.toAscii_multiList( subgoalAttList )

  # ---------------------------------------- #
  # replace all subgoal atts not appearing in goal att list
  # with wildcards
  for att in subgoalAttList :

    attID   = att[0]
    attName = att[1]
    attType = att[2]

    if attName in atts :
      continue

    else :
      if not attName == "_" :
        replaceWithWildcard( rid, sid, attID, cursor )


##########################
#  REPLACE WITH WILCARD  #
##########################
def replaceWithWildcard( rid, sid, attID, cursor ) :
  attName = "_"
  cursor.execute( "UPDATE SubgoalAtt SET attName='" + attName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "' AND attID=='" + str( attID ) + "'" )


###########################
#  HANDLE CLOCK SUBGOALS  #
###########################
# check clock for existential attributes, regardless of whether clock is negative or positive.
# if existential attributes exist for either SndTime or DelivTime, 
# add an additional subgoal to the rule.
def handleClockSubgoals( EOT, rid, sid, cursor ) :

  # ------------------------------------ #
  # get all goal atts
  cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
  gattData = cursor.fetchall()
  gattData = tools.toAscii_multiList( gattData )

  # ------------------------------------ #
  # get all subgoal atts
  cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
  sattData = cursor.fetchall()
  sattData = tools.toAscii_multiList( sattData )

  # ------------------------------------ #
  # check if sugoal att is existnetial
  gattList = [ att[1] for att in gattData ]
  sattList = [ att[1] for att in sattData ]

  # ------------------------------------ #
  for i in range( 0, len(sattList) ) :

    att = sattList[i]

    # check if clock subgoal att appears in goal att list
    # thus, att is universal
    if att in gattList :
      continue

    # otherwise, clock subgoal att does not appear in goal
    # att list. thus, att is existential.
    else :
      if att == "SndTime" or att == "DelivTime" :
        addAdditionalTimeDom( EOT, att, rid, cursor )

      else :
        replaceWithWildcard( rid, sid, i, cursor )


#############################
#  ADD ADDITIONAL TIME DOM  #
#############################
def addAdditionalTimeDom( EOT, att, rid, cursor ) :

  sid            = tools.getID()
  subgoalTimeArg = ""
  attID          = 0 # dom subgoals are fixed at arity 1
  attType        = "int"
  argName        = ""

  if att == "SndTime" :
    subgoalName = "dom_sndtime"
    attName     = "SndTime"

  else : # att == "DelivTime"
    subgoalName = "dom_delivtime"
    attName     = "DelivTime"

  # ------------------------------------- #
  # add info to Subgoals relation
  cursor.execute( "INSERT INTO Subgoals VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')" )

  # ------------------------------------- #
  # add info to SubgoalAtt relation
  cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

  # ------------------------------------- #
  # add info to SubgoalAddArgs relation
  cursor.execute( "INSERT INTO SubgoalAddArgs VALUES ('" + rid + "','" + sid + "','" + argName + "')" )

  # ------------------------------------- #
  # add info to SubgoalAddArgs relation
  # add relevant new facts.
  # dom ranges over all ints between 1 and EOT.
  name    = subgoalName
  timeArg = 1   # all dom facts are true starting at time 1
  attType = "int"
  attID   = 0

  for i in range( 1, EOT+1 ) :
    fid = tools.getID()

    # ------------------------------------- #
    # add info to Fact relation
    cursor.execute( "INSERT INTO Fact VALUES ('" + fid + "','" + name + "','" + str( timeArg ) + "')" )

    # ------------------------------------- #
    # add info to FactAtt
    attName = i
    cursor.execute( "INSERT INTO FactAtt VALUES ('" + fid + "','" + str( attID ) + "','" + str( attName ) + "','" + attType + "')" )


##############
#  IS CLOCK  #
##############
# check if subgoal at sid in rule rid is a clock subgoal
def isClock( rid, sid, cursor ) :

  cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
  subName = cursor.fetchone()
  subName = tools.toAscii_str( subName )

  if subName == "clock" :
    return True

  return False


#########################
#  ADD DOMAIN SUBGOALS  #
#########################
# add domain constraints to universal attributes per rewritten rule.
def addDomainSubgoals( parentRID, posName, nameRIDS, newDMRIDList, pResults, cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print "   ... running ADD DOMAIN SUBGOALS ..."

  # -------------------------------------------------- #
  # make sure results exist.                           #
  # -------------------------------------------------- #
  attDomsMap = getAttDoms( parentRID, posName, nameRIDS, newDMRIDList, pResults, cursor )

  if not attDomsMap == {} :

    # -------------------------------------------------- #
    # build domain EDBs and add to facts tables.         #
    # -------------------------------------------------- #
    # get base att domain name
    domNameBase = getAttDomNameBase( posName )

    # save EDB facts
    newDomNames = saveDomFacts( domNameBase, attDomsMap, cursor )

    # -------------------------------------------------- #
    # add attribute domain subgoals to all new DM rules. #
    # -------------------------------------------------- #
    addSubgoalsToRules( newDomNames, newDMRIDList, cursor )


##################
#  GET ATT DOMS  #
##################
def getAttDoms( parentRID, posName, nameRIDS, newDMRIDList, pResults, cursor ) :

  print "================================================"
  print "... running GET ATT DOMS from negativeWrites ..."
  print "================================================"

  print "parent rule    : " + dumpers.reconstructRule( parentRID, cursor )
  print "posName        : " + posName
  print "nameRIDS rules :"
  for rid in nameRIDS :
    print dumpers.reconstructRule( rid, cursor )

  attDomsMap = {}

  #----------------------------------------------------------#
  #if "missing_log" in posName[0:11] :
  #  print "parent Rule:"
  #  print dumpers.reconstructRule( parentRID, cursor )

  #  print "nameRIDS"
  #  for rid in nameRIDS :
  #    print dumpers.reconstructRule( rid, cursor )

  #  print "newDMRIDList"
  #  for rid in newDMRIDList :
  #    print dumpers.reconstructRule( rid, cursor )
  #----------------------------------------------------------#

  # ---------------------------------------------------- #
  # get the parent rule name                             #
  # ---------------------------------------------------- #
  parentName = getParentName( parentRID, cursor )

  print "parentName = " + parentName
  print "pResults[ " + parentName + " ] :"
  print pResults[ parentName ]

  # ---------------------------------------------------- #
  # get the domain for each attribute of positive rule,  #
  # as determined in pResults.                           #
  # ---------------------------------------------------- #
  attDomsMap = getParentAttDomains( pResults[ parentName ] )

  # ---------------------------------------------------- #
  # empty domain map means parent rule didn't fire.      #
  # fill doms with default values.                       #
  # ---------------------------------------------------- #
  if attDomsMap == {} :
    print "filling defaults..."
    attDomsMap = fillDefaults( newDMRIDList, cursor )

  #----------------------------------------------------------#
  #if "missing_log" in posName[0:11] :
  #  print "attDomsMap = " + str( attDomsMap )
  #  tools.bp( __name__, inspect.stack()[0][3], "shit" )
  #----------------------------------------------------------#

  print "attDomsMap = " + str( attDomsMap )

  return attDomsMap


###################
#  FILL DEFAULTS  #
###################
def fillDefaults( newDMRIDList, cursor ) :

  # get goal arity
  chooseAnRID = newDMRIDList[0]
  cursor.execute( "SELECT attID,attType FROM GoalAtt WHERE rid=='" + chooseAnRID + "'" )
  data = cursor.fetchall()
  data = tools.toAscii_multiList( data )

  lastAttID = data[-1][0]
  arity     = lastAttID + 1

  domMap = {}
  for i in range( 0, arity ) :

    attType = data[ i ][ 1 ]

    if attType == "string" :
      col = [ "_DEFAULT_STRING_" ]
    else :
      col = [ 99999999999 ]

    domMap[ i ] = col

  return domMap


#####################
#  GET PARENT NAME  #
#####################
def getParentName( parentRID, cursor ) :

  cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + parentRID + "'" )
  parentName = cursor.fetchone()
  parentName = tools.toAscii_str( parentName )

  return parentName


###########################
#  ADD SUBGOALS TO RULES  #
###########################
# add domain subgoals to new demorgan's rules.
def addSubgoalsToRules( newDomNames, newDMRIDList, cursor ) :

  for rid in newDMRIDList :

    print "this rule : " + dumpers.reconstructRule( rid, cursor )

    # ----------------------------------- #
    # get goal att list
    cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + rid + "'" )
    goalAttList = cursor.fetchall()
    goalAttList = tools.toAscii_multiList( goalAttList )

    print "goalAttList = " + str( goalAttList )
    print "newDomNames = " + str( newDomNames )

    # ----------------------------------- #
    # map att names to att indexes
    attNameIndex = {}
    for att in goalAttList :
      attID   = att[0]
      attName = att[1]
      attType = att[2]

      attIndex = attName.replace( "A", "" )

      attNameIndex[ attName ] = attIndex

    subNum = 0 
    for subName in newDomNames :

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

      print "subNum = " + str(subNum)
      print "subName = " + str( subName )

      att     = goalAttList[ subNum ]
      attID   = 0       # domain subgoals have arity 1
      attName = att[1]
      attType = att[2]

      cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

      subNum += 1


####################
#  SAVE DOM FACTS  #
####################
def saveDomFacts( domNameBase, attDomsMap, cursor ) :

  print "++++++++++++++++++++++++++++++++++++++++++++++++++"
  print "... running SAVE DOM FACTS from negativeWrites ..."
  print "++++++++++++++++++++++++++++++++++++++++++++++++++"

  if domNameBase[0:10] == "dom_clock_" :
    print "domNameBase = " + domNameBase
    print "attDomsMap = " + str( attDomsMap )
    #tools.bp( __name__, inspect.stack()[0][3], "stop here" )

  newDomNames = []
  for att in attDomsMap :
    attID = att
    dom   = attDomsMap[ att ]

    # -------------------------------------------- #
    # insert new fact data
    for data in dom :

      # ............................................ #
      # generate new fact id
      fid = tools.getID()

      # ............................................ #
      # create full fact name
      factName = domNameBase + str( attID ) 

      # ............................................ #
      # all dom facts are true starting at time 1
      timeArg = '1'

      # ............................................ #
      # insert new fact metadata

      #if factName == "bcast" :
      #  print "/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/"
      #  print "  CHECK THIS BCAST INSERT!!!!"

      #print "INSERT INTO Fact VALUES ('" + fid + "','" + factName + "','" + timeArg + "')"
      cursor.execute( "INSERT INTO Fact VALUES ('" + fid + "','" + factName + "','" + timeArg + "')" )

      # ............................................ #
      # set type
      if tools.isInt(data) :
        attType = 'int'
      else :
        attType = 'string'
        data    = '"' + data + '"'

      # ............................................ #
      # perform insertion
      thisID = 0 # contant because domain relations are unary.
      #print "INSERT INTO FactAtt VALUES ('" + fid + "','" + str(thisID) + "','" + data + "','" + attType + "')"
      cursor.execute( "INSERT INTO FactAtt VALUES ('" + fid + "','" + str(thisID) + "','" + str( data ) + "','" + attType + "')" )

    # -------------------------------------------- #
    # collect domain subgoal names for convenience
    if not factName in newDomNames :
      newDomNames.append( factName )

  return newDomNames


###########################
#  GET ATT DOM NAME BASE  #
###########################
def getAttDomNameBase( name ) :
  return "dom_" + name + "_att"


############################
#  GET PARENT ATT DOMAINS  #
############################
def getParentAttDomains( results ) :

  #print "results = " + str( results )

  if not results == [] :

    # get tuple arity
    arity = len( results[0] )

    attDomsMap = {}
    attID = 0
    for i in range( 0, arity ) :
      col = []
      for tup in results :
        if not tup[i] in col :
          col.append( tup[i] )
      attDomsMap[ i ] = col

    return attDomsMap

  else :
    return {}


#####################
#  SHIFT ARITH OPS  #
#####################
# given list of rids for the IDB rule set to be negated.
# for rules with arithmetic operations in the head,
# rewrite the rules into a series of separate, but sematically
# equivalent rules.
def shiftArithOps( nameRIDs, cursor ) :

  newRIDs = []

  # for each rule, check if goal contains an arithmetic operation
  for rid in nameRIDs :
    cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
    attData = cursor.fetchall()
    attData = tools.toAscii_multiList( attData )

    for att in attData :
      attID   = att[0]
      attName = att[1]

      if containsOp( attName ) :

        # compose raw attribute with function call 
        # (only supporting arithmetic ops at the moment)
        decomposedAttName = getOp( attName )  # [ lhs, op, rhs ]
        lhs = decomposedAttName[0]
        op  = decomposedAttName[1]
        rhs = decomposedAttName[2]

        # build substitute goal attribute variable
        newAttName = lhs + "0"

        # replace the goal attribute variable
        replaceGoalAtt( newAttName, attID, rid, cursor )

        # rewrite subgoals containing the universal variable included in the equation
        # with unique subgoals referencing new IDB definitions.
        newArithRuleRIDs = arithOpSubgoalRewrites( rid, newAttName, lhs, attName, cursor )
        newRIDs.extend( newArithRuleRIDs )

  return newRIDs

###############################
#  ARITH OP SUBGOAL REWRITES  #
###############################
# given the id for one of the rules targeted for NegativeWrites,
# the string replacing the arithmetic expression in the goal,
# and the universal attribute appearing in an arithmetic expression
# in the head.
# replace the subgoals containing the universal attribute with new subgoals
# such that the new subgoals have unique names and the new replacement attribute 
# replace the universal attribute in the subgoal.
#
def arithOpSubgoalRewrites( rid, newAttName, oldExprAtt, oldExpr, cursor ) :

  newRIDs = []

  # get subgoal info
  cursor.execute( "SELECT Subgoals.sid,Subgoals.subgoalName,attID FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + rid + "' AND Subgoals.rid==SubgoalAtt.rid AND attName=='" + oldExprAtt + "'" )
  sidData = cursor.fetchall()
  sidData = tools.toAscii_multiList( sidData )

  # ............................................. #
  # remove duplicates
  tmp = []
  for sid in sidData :
    if not sid in tmp :
      tmp.append( sid )
  sidData = tmp
  # ............................................. #

  for data in sidData :
    sid         = data[0]
    subgoalName = data[1]
    attID       = data[2]

    # --------------------------------------------- #
    # replace subgoal name with unique new name 
    # connecting to another set of IDB rule(s)

    # get rule name for this rid
    cursor.execute( "SELECT goalName FROM Rule WHERE rid=='" + rid + "'" )
    ruleName = cursor.fetchone()
    ruleName = tools.toAscii_str( ruleName )

    # generate new unique subgoal name
    newSubgoalName = ruleName + "_" + subgoalName + "_" + tools.getID_4() + "_arithoprewrite"

    cursor.execute( "UPDATE Subgoals SET subgoalName=='" + newSubgoalName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

    # --------------------------------------------- #
    # replace universal attribute in subgoals
    cursor.execute( "UPDATE SubgoalAtt SET attName=='" + newAttName + "' WHERE rid=='" + rid + "' AND attID=='" + str( attID ) + "' AND sid=='" + sid + "'" )

    # --------------------------------------------- #
    # build new subgoal IDB rules
    newRID = arithOpSubgoalIDBWrites( rid, sid, newSubgoalName, subgoalName, oldExprAtt, oldExpr, attID, cursor )
    newRIDs.append( newRID )

  return newRIDs


#################################
#  ARITH OP SUBGOAL IDB WRITES  #
#################################
# write the new IDB rules supporting the distribution of equations
# across rule subgoals.
def arithOpSubgoalIDBWrites( oldRID, targetSID, newSubgoalName, oldSubgoalName, oldExprAtt, oldExpr, attID, cursor) :

  # --------------------------------------------- #
  # generate new rule ID                          #
  # --------------------------------------------- #
  newRID = tools.getID()

  # --------------------------------------------- #
  # insert new rule data                          #
  # --------------------------------------------- #
  rid         = newRID
  goalName    = newSubgoalName
  goalTimeArg = ""
  rewritten   = "False"
  cursor.execute( "INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + rid + "','" + goalName + "','" + goalTimeArg + "','" + rewritten + "')" )

  # --------------------------------------------- #
  # insert new rule data                          #
  # --------------------------------------------- #
  # get attribute data from original subgoal
  cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid=='" + oldRID + "' AND sid=='" + targetSID + "'" )
  data = cursor.fetchall()
  data = tools.toAscii_multiList( data )

  # ............................................. #
  # define the att list for the only subgoal 
  # in the new rule body and replace new goal
  # att str with old goal att str

  subgoalAttData             = data
  subgoalAttData[ attID ][1] = oldExprAtt

  # ............................................. #
  # resolve wildcard attributes to actual 
  # variables.

  subgoalAttData = resolveWildcardAtts( subgoalAttData )

  # ............................................. #
  # define goal att list and 
  # replace old arithmetic expression

  # need this shit to prevent mutating subgoalAttData
  goalAttData = []
  for thing in data :
    thisThing = [ i for i in thing ]
    goalAttData.append( thisThing )
  goalAttData[attID][1] = oldExpr

  # ............................................. #
  # perform inserts

  # goal attributes
  for att in goalAttData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]
    cursor.execute( "INSERT INTO GoalAtt (rid, attID, attName, attType) VALUES ('" + rid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

  # subgoal
  sid            = tools.getID()
  subgoalName    = oldSubgoalName
  subgoalTimeArg = ""
  cursor.execute( "INSERT INTO Subgoals (rid, sid, subgoalName, subgoalTimeArg) VALUES ('" + rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')" )

  # subgoal attributes
  for att in subgoalAttData :
    attID   = att[0]
    attName = att[1]
    attType = att[2]
    cursor.execute( "INSERT INTO SubgoalAtt (rid, sid, attID, attName, attType) VALUES ('" + rid + "','" + sid + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )

  # ............................................. #
  # resolve types
  newRule = Rule.Rule( newRID, cursor )
  newRule.setAttTypes()

  #if "log_log_" in newSubgoalName[0:8] and "_log_" in newSubgoalName[12:17] :
  #  tools.bp( __name__, inspect.stack()[0][3], "here" )

  return newRID # means building the rule object twice. kind of redundant...


###########################
#  RESOLVE WILDCARD ATTS  #
###########################
# resolve wildcard attributes to actual variables b/c
# these attributes are copied directly into the goal 
# attribute list of this new rule.
def resolveWildcardAtts( subgoalAttData ) :
  counter = 0
  for data in subgoalAttData :

    if data[1] == "_" :
      data[1] = "B" + str( counter )
      counter += 1

  return subgoalAttData


##########################
#  SHIFT FUNCTION CALLS  #
##########################
# given list of rids for IDB rule set to be negated.
# for rules with function calls in the head, shift 
# the function call to an eqn in the body.
def shiftFunctionCalls( nameRIDs, cursor ) :

  # for each rule, check if goal contains a function call
  for rid in nameRIDs :
    cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
    attData = cursor.fetchall()
    attData = tools.toAscii_multiList( attData )

    for att in attData :
      attID   = att[0]
      attName = att[1]

      if containsOp( attName ) :

        # compose raw attribute with function call 
        # (only supporting arithmetic ops at the moment)
        decomposedAttName = getOp( attName )  # [ lhs, op, rhs ]
        lhs = decomposedAttName[0]
        op  = decomposedAttName[1]
        rhs = decomposedAttName[2]

        # build substitute goal attribute variable
        newAttName = lhs + "0"

        # generate appropriate equation using a new variable 
        # for the corresponding goal attribute.
        eqn = generateEqn( newAttName, lhs, op, rhs, rid, cursor )

        # replace the goal attribute variable
        replaceGoalAtt( newAttName, attID, rid, cursor )

        # add equation to rule
        addEqn( eqn, rid, cursor )


##################
#  GENERATE EQN  #
##################
# generate appropriate equation using a new variable 
# for the corresponding goal attribute.
def generateEqn( newAttName, lhs, op, rhs, rid, cursor ) :

  eqn = newAttName + "==" + lhs + op + rhs

  return eqn


######################
#  REPLACE GOAL ATT  #
######################
# replace the goal attribute variable
def replaceGoalAtt( newAttName, attID, rid, cursor ) :

  cursor.execute( "UPDATE GoalAtt SET attName=='" + newAttName + "' WHERE rid=='" + rid + "' AND attID=='" + str( attID ) + "'" )


#############
#  ADD EQN  #
#############
# add equation to rule
def addEqn( eqn, rid, cursor ) :

  # generate new random identifier
  eid = tools.getID()

  # add equation for this rule
  cursor.execute( "INSERT INTO Equation VALUES ('" + rid + "','" + eid + "','" + eqn + "')" )


######################################
#  SET UNIFORM UNIVERSAL ATTRIBUTES  #
######################################
# rewrite original rules with uniform universal attribute variables
def setUniformUniversalAttributes( rids, cursor ) :

  print "===================================================================="
  print "... running SET UNIFORM UNIVERSAL ATTRIBUTES from negativeWrites ..."
  print "===================================================================="

  print "positive rule version rids : " + str( rids )

  # ------------------------------------------------------- #
  # get arity of this IDB                                   #
  # ------------------------------------------------------- #
  arity = None

  #print "rids = " + str( rids )
  #for rid in rids :
  #  print dumpers.reconstructRule( rid, cursor )

  for rid in rids :
    cursor.execute( "SELECT max(attID) FROM GoalAtt WHERE rid=='" + rid + "'" )
    maxID = cursor.fetchone()
    arity = maxID[0]

  # ------------------------------------------------------- #
  # generate list of uniform attribute names of same arity  #
  # ------------------------------------------------------- #
  uniformAttributeList = []

  for i in range(0, arity) :
    uniformAttributeList.append( "A" + str( i ) )

  uniformAttributeList = tuple( uniformAttributeList ) # make immutable. fixes weird list update referencing bug.

  # ------------------------------------------------------- #
  # perform variable substitutions for rules accordingly    #
  # ------------------------------------------------------- #
  for rid in rids :

    uniformList = list( uniformAttributeList ) # make mutable
    variableMap = {}

    print "arity : " + str( arity )
    print "rule : " + dumpers.reconstructRule( rid, cursor )

    for i in range(0, arity) :

      # /////////////////////////// #
      # populate variable map
      cursor.execute( "SELECT attName FROM GoalAtt WHERE rid=='" + rid + "' AND attID=='" + str(i) + "'" )
      attName = cursor.fetchone()
      attName = tools.toAscii_str( attName )

      # handle goal attributes with operators
      if containsOp( attName ) :
        decomposedAttName = getOp( attName )  # [ lhs, op, rhs ]

        lhs = decomposedAttName[0]
        op  = decomposedAttName[1]
        rhs = decomposedAttName[2]

        variableMap[ lhs ] = uniformList[i]
        uniformList[i] = uniformList[i] + op + rhs

      else :
        variableMap[ attName ] = uniformList[i]

      # /////////////////////////// #
      # substitutions in head       #
      # /////////////////////////// #
      cursor.execute( "UPDATE GoalAtt SET attName=='" + uniformList[i] + "' WHERE rid=='" + rid + "' AND attID=='" + str(i) + "'" )

    # /////////////////////////// #
    # substitutions in subgoals   #
    # /////////////////////////// #

    # get sids for this rule
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid=='" + rid + "'" )
    sids = cursor.fetchall()
    sids = tools.toAscii_list( sids )

    for sid in sids :

      # map attIDs to attNames
      attMap = {}
      cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + rid + "' AND sid=='" + sid + "'"  )
      attData = cursor.fetchall()
      attData = tools.toAscii_multiList( attData )

      for att in attData :
        attID   = att[0]
        attName = att[1]

        if attName in variableMap :
          cursor.execute( "UPDATE SubgoalAtt SET attName=='" + variableMap[ attName ] + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "' AND attID=='" + str( attID ) + "'" )


    # /////////////////////////// #
    # substitutions in equations  #
    # /////////////////////////// #

    # get eids for this rule
    cursor.execute( "SELECT eid FROM Equation WHERE rid=='" + rid + "'" )
    eids = cursor.fetchall()
    eids = tools.toAscii_list( eids )

    for eid in eids :

      # decompose eqn into components <- assumes structure
      # of the form : <lhsVariable>=<rhsExpression>

      cursor.execute( "SELECT eqn FROM Equation WHERE rid=='" + rid + "' AND eid=='" + eid + "'" )
      eqn = cursor.fetchone()
      eqn = tools.toAscii_str( eqn )

      eqn = eqn.split( "==" )

      lhs_eqn = eqn[0]
      rhs_eqn = eqn[1]

      decomposedAttName = getOp( rhs_eqn )  # [ lhs, op, rhs ]
      lhs_expr = decomposedAttName[0]
      op       = decomposedAttName[1]
      rhs_expr = decomposedAttName[2]

      # check contents of eqn for goal atts
      # save existential vars for later annotation of "__KEEP__" string
      # to prevent wildcard replacement in future stages.
      existentialVarMap = {}
      for var in variableMap :

        # ************************************ #
        # check lhs of eqn is a goal att
        if tools.isInt( lhs_eqn ) : 
          pass
        else :
          if var in lhs_eqn :
            lhs_eqn = variableMap[ var ]

          else : # it's an existential var

            # generate new existential var
            newExistentialVar = generateNewVar( lhs_eqn )

            # save to map
            existentialVarMap[ lhs_eqn ] = newExistentialVar

        # ************************************ #
        # check lhs of rhs expression
        if tools.isInt( lhs_expr ) : 
          pass
        else :
          if var in lhs_expr :
            lhs_expr = variableMap[ var ]
          else : # it's an existential var

            # generate new existential var
            newExistentialVar = generateNewVar( lhs_expr )

            # save to map
            existentialVarMap[ lhs_expr ] = newExistentialVar

        # ************************************ #
        # check rhs of rhs expression
        if tools.isInt( rhs_expr ) : 
          pass
        else :
          if var in rhs_expr :
            rhs_expr = variableMap[ var ]
          else : # it's an existential var

            # generate new existential var
            newExistentialVar = generateNewVar( lhs_eqn )

            # save to map
            existentialVarMap[ rhs_expr ] = newExistentialVar
        # ************************************ #

      # generate new equation using the variable substitutions, if applicable
      if lhs_expr in existentialVarMap :
        lhs_expr = existentialVarMap[ lhs_expr ]
      if rhs_expr in existentialVarMap :
        rhs_expr = existentialVarMap[ rhs_expr ]

      newEqn = lhs_eqn + "==" + lhs_expr + op + rhs_expr

      # replace old equation
      cursor.execute( "UPDATE Equation SET eqn=='" + newEqn + "' WHERE rid=='" + rid + "' AND eid=='" + eid + "'" )


      # ====================================================================== #
      # preserve existential attributes appearing in the eqn across the rule
      # ====================================================================== #

      for sid in sids :

        # get attribs
        cursor.execute( "SELECT attID,attName FROM SubgoalAtt WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
        attData = cursor.fetchall()
        attData = tools.toAscii_multiList( attData )

        for att in attData :
          attID   = att[0]
          attName = att[1]

          if attName in existentialVarMap :
            newAttName = existentialVarMap[ attName ]
            cursor.execute( "UPDATE SubgoalAtt SET attName=='" + newAttName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "' AND attID=='" + str( attID ) + "'" )


######################
#  GENERATE NEW VAR  #
######################
def generateNewVar( oldVar ) :
  return oldVar + "__KEEP__" #+ tools.getID_4()


#################
#  CONTAINS OP  #
#################
def containsOp( attName ) :

  flag = False
  for op in arithOps :
    if op in attName :
      flag = True

  return flag


############
#  GET OP  #
############
def getOp( attName ) :

  for op in arithOps :

    if op in attName :
      s = attName.split( op )
      return [ s[0], op, s[1] ]

    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : attName '" + attName + "' does not contain an arithOp.\nPlease check if universe exploded. Aborting..."  )


#################
#  PRINT RULES  #
#################
def printRules( rids, cursor ) :
  for rid in rids :
    print dumpers.reconstructRule( rid, cursor )


##################
#  GET ALL RIDS  #
##################
# return the list of rids for all rules in the program currently stored in cursor.
def getAllRuleRIDs( cursor ) :
  cursor.execute( "SELECT rid FROM Rule" )
  rids = cursor.fetchall()
  rids = tools.toAscii_list( rids )
  return rids


###############################
#  RULE CONTAINS NEGATED IDB  #
###############################
# check if the given rule contains a negated IDB
def ruleContainsNegatedIDB( rid, cursor ) :

  cursor.execute( "SELECT Subgoals.subgoalName FROM Subgoals,SubgoalAddArgs WHERE Subgoals.rid='" + rid + "' AND Subgoals.rid==SubgoalAddArgs.rid AND Subgoals.sid==SubgoalAddArgs.sid AND argName=='notin'" )
  negatedSubgoals = cursor.fetchall()
  negatedSubgoals = tools.toAscii_list( negatedSubgoals )

  flag = False

  for subgoalName in negatedSubgoals :

    # skip arith op rewrites for now.
    if "_arithoprewrite" in subgoalName :
      pass

    # skip edb rewrites
    elif "_edbrewrite" in subgoalName :
      pass

    elif isIDB( subgoalName, cursor ) :
      flag = True

  return flag


############
#  IS IDB  #
############
# check if the given string corresponds to the name of a rule in an input program.
# if so, then the string corresponds to an IDB relation
def isIDB( subgoalName, cursor ) :

  cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + subgoalName + "'" )
  rids = cursor.fetchall()
  rids = tools.toAscii_list( rids )

  if len( rids ) > 0 :
    return True
  else :
    return False


#########################
#  REWRITE PARENT RULE  #
#########################
# replace negated subgoals in parent rules with positive counterparts.
# returns name of negated subgoal replaced by positive subgoal and 
# the parent RID.
def rewriteParentRule( rid, cursor ) :

  negatedIDBNames = []

  # .................................................... #
  # get rule name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid='" + rid + "'" )
  goalName = cursor.fetchone()
  goalName = tools.toAscii_str( goalName )

  # .................................................... #
  # get list of negated IDB subgoals
  cursor.execute( "SELECT Subgoals.sid,Subgoals.subgoalName FROM Subgoals,SubgoalAddArgs WHERE Subgoals.rid='" + rid + "' AND Subgoals.rid==SubgoalAddArgs.rid AND Subgoals.sid==SubgoalAddArgs.sid AND argName=='notin'" )
  negatedSubgoals = cursor.fetchall()
  negatedSubgoals = tools.toAscii_multiList( negatedSubgoals )

  #print "negatedSubgoals = " + str( negatedSubgoals )

  # .................................................... #
  # substitute with appropriate positive counterpart
  for subgoal in negatedSubgoals :
    sid  = subgoal[0]
    name = subgoal[1]

    if "_arithoprewrite" in name :
      pass

    elif isIDB( name, cursor ) :

      positiveName = "not_" + name + "_from_" + goalName
  
      #print "positiveName = " + positiveName
  
      # .................................................... #
      # substitute in positive subgoal name
      cursor.execute( "UPDATE Subgoals SET subgoalName=='" + positiveName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
  
      # .................................................... #
      # erase negation on this subgoal
      cursor.execute( "UPDATE SubgoalAddArgs SET argName=='' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )
  
      # .................................................... #
      # save for return data
      negatedIDBNames.append( [ name, rid ] )

  # .................................................... #
  # remove duplicates
  negatedIDBNames = removeDups( rid, negatedIDBNames )

  return negatedIDBNames


#################
#  REMOVE DUPS  #
#################
def removeDups( parentRID, negatedIDBNames ) :

  tmp = []
  for data in negatedIDBNames :
    name = data[0]
    if not name in tmp :
      tmp.append( name )

  return [ [ x, parentRID ] for x in tmp ]


########################
#  GET RIDS FROM NAME  #
########################
# return the list of all rids associated with a particular goal name.
def getRIDsFromName( name, cursor ) :

  cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + name + "'" )
  ridList = cursor.fetchall()
  ridList = tools.toAscii_list( ridList )

  return ridList


#####################
#  APPLY DEMORGANS  #
#####################
# perform the rewrites on the negated IDB rules.
# data for new rules are stored directly in the IR database.
def applyDeMorgans( parentRID, nameRIDs, cursor ) :
  return deMorgans.doDeMorgans( parentRID, nameRIDs, cursor )



##############
#  EVALUATE  #
##############
def evaluate( COUNTER, cursor ) :

  # translate into c4 datalog
  allProgramLines = c4_translator.c4datalog( cursor )

  # run program
  print "call c4 wrapper from negativeWrites"
  results_array = c4_evaluator.runC4_wrapper( allProgramLines )

  #print "FROM evaluate in negativeWrites : results_array :"
  #print results_array

  # ----------------------------------------------------------------- #
  # dump evaluation results locally
  eval_results_dump_dir = os.path.abspath( os.getcwd() ) + "/data/"

  # make sure data dump directory exists
  if not os.path.isdir( eval_results_dump_dir ) :
    print "WARNING : evalulation results file dump destination does not exist at " + eval_results_dump_dir
    print "> creating data directory at : " + eval_results_dump_dir
    os.system( "mkdir " + eval_results_dump_dir )
    if not os.path.isdir( eval_results_dump_dir ) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unable to create evaluation results dump directory at " + eval_results_dump_dir )
    print "...done."

  # otherwise, data dump directory exists
  eval_results_dump_to_file( COUNTER, results_array, eval_results_dump_dir )

  # ----------------------------------------------------------------- #
  # parse results into a dictionary
  parsedResults = tools.getEvalResults_dict_c4( results_array )

  #print "FROM evaluate in negativeWrites : parsedResults :"
  #print parsedResults

  # ----------------------------------------------------------------- #

  return parsedResults


###############################
#  EVAL RESULTS DUMP TO FILE  #
###############################
def eval_results_dump_to_file( COUNTER, results_array, eval_results_dump_dir ) :

  eval_results_dump_file_path = eval_results_dump_dir + "eval_dump_" + str( COUNTER ) + ".txt"

  # save new contents
  f = open( eval_results_dump_file_path, "w" )

  for line in results_array :

    print line

    # output to file
    f.write( line + "\n" )

  f.close()


#########
#  EOF  #
#########
