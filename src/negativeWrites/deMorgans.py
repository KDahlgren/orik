#!/usr/bin/env python

'''
deMorgans.py
   Define the functionality for collecting the provenance of negative subgoals.
'''

import inspect, os, string, sys
import sympy

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from dedt  import Rule
from utils import tools, dumpers
# ------------------------------------------------------ #


#############
#  GLOBALS  #
#############
NEGATIVEWRITES_DEBUG = tools.getConfig( "DEDT", "NEGATIVEWRITES_DEBUG", bool )

arithOps = [ "+", "-", "*", "/" ]


################
#  DO MORGANS  #
################
# generates a set of new rules by applying deMorgan's law on the input rule set
# and adds domain constraint subgoals where appropriate. 
def doDeMorgans( parentRID, ruleRIDs, cursor ) :

  # ----------------------------------------------------------- #
  # get data for naming stuff
  # ----------------------------------------------------------- #
  # parent name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid='" + parentRID + "'" )
  parentName = cursor.fetchall()
  parentName = tools.toAscii_str( parentName[0] )

  # this IDB name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid='" + ruleRIDs[0] + "'" )
  thisIDBName = cursor.fetchall()
  thisIDBName = tools.toAscii_str( thisIDBName[0] )

  # ----------------------------------------------------------- #
  # combine all rules for each rule name into a single 
  # sympy formula string
  # ----------------------------------------------------------- #
  # associate each subgoal per rule for this IDB definition with an identifier
  # and map to [ rid, [ sign, sid ] ] arrays
  predicateToID_map     = {}

  # map rids,sid pairs to predicate identifiers (essentially the reverse of the above mapping)
  ridSidToPredicate_map = {}

  # ////////////////////////////////////////// #
  # get all rule data
  for rid in ruleRIDs :

    # get list of all sids for this rid
    # filter out sids for domain subgoals
    cursor.execute( "SELECT sid FROM Subgoals WHERE rid=='" + rid + "' AND NOT subgoalName LIKE 'dom_%'" )
    sidList = cursor.fetchall()
    sidList = tools.toAscii_list( sidList )

    # map sids to sign for this rule
    signMap = {}
    for sid in sidList :
      cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid='" + rid + "' AND sid='" + sid + "'" )
      sign = cursor.fetchone()
      if sign :
        sign = tools.toAscii_str( sign )
      signMap[ sid ] = sign

    for sid in sidList :
      sign = signMap[ sid ]

      # get a random identifier string
      predID = tools.getID()

      # map predIDs to rids and sids
      predicateToID_map[ predID ] = [ rid, [ sign, sid ] ]

      # map rids and sids to predIDs
      if sign == "notin" :
        key = rid + ",_NEG_" + sid
      else :
        key = rid + "," + sid
      ridSidToPredicate_map[ key ] = predID

  # ----------------------------------------------------------- #
  # simplify DNF
  simplified_negFmla = getDNFFmla_v1( ridSidToPredicate_map )
  #simplified_negFmla = getDNFFmla_v2( ridSidToPredicate_map )

  # ----------------------------------------------------------- #
  # save a new rule to IR db per disjunct
  newDMRIDList = setNewRules( parentName, thisIDBName, simplified_negFmla, predicateToID_map, cursor )

  # ----------------------------------------------------------- #

  return newDMRIDList


#####################
#  GET DNF FMLA V2  #
#####################
def getDNFFmla_v2( ridSidToPredicate_map ) :

  # ////////////////////////////////////////// #
  # convert to sympy formula
  ruleConjuncts_map = {}
  for key in ridSidToPredicate_map :
    predID = ridSidToPredicate_map[ key ]
    key    = key.split( "," )
    rid    = key[0]
    sid    = key[1]
    sign   = None

    if "_NEG_" in sid :
      sid  = sid.replace( "_NEG_", "" )
      sign = "_NEG_"

    if rid in ruleConjuncts_map :
      currConjunct_str = ruleConjuncts_map[ rid ]
      if sign :
        ruleConjuncts_map[ rid ] = currConjunct_str + " & ~( " + predID + " )"
      else :
        ruleConjuncts_map[ rid ] = currConjunct_str + " & " + predID
    else :
      if sign :
        ruleConjuncts_map[ rid ] = "~( " + predID + " )"
      else :
        ruleConjuncts_map[ rid ] = predID

  # ----------------------------------------------------------------- #
  # decrease work on sympy call by negating clauses individually 
  # and taking the conjunction of the negated clauses:
  #

  # apply negations and DNF simplifications on clauses individually
  for rid in ruleConjuncts_map :
    conjunct_str = ruleConjuncts_map[ rid ]
    ruleConjuncts_map[ rid ] = sympy.to_dnf( "~ ( " + conjunct_str + " )" )

  # build negative DNF fmla
  # by AND'ing together negated clauses.
  negFmla = None
  for key in ruleConjuncts_map :
    if negFmla :
      negFmla += " & " + str( ruleConjuncts_map[key] )
    else :
      negFmla = str( ruleConjuncts_map[key] )

  print "negFmla = " + negFmla

  ## simplify DNF
  #simplified_negFmla = sympy.to_dnf( negFmla )
  #return simplified_negFmla

  return negFmla


#####################
#  GET DNF FMLA V1  #
#####################
def getDNFFmla_v1( ridSidToPredicate_map ) :

  # ////////////////////////////////////////// #
  # convert to sympy formula
  ruleConjuncts_map = {}
  for key in ridSidToPredicate_map :
    predID = ridSidToPredicate_map[ key ]
    key    = key.split( "," )
    rid    = key[0]
    sid    = key[1]
    sign   = None
    if "_NEG_" in sid :
      sid  = sid.replace( "_NEG_", "" )
      sign = "_NEG_"

    if rid in ruleConjuncts_map :
      currConjunct_str = ruleConjuncts_map[ rid ]
      if sign :
        ruleConjuncts_map[ rid ] = currConjunct_str + " & ~( " + predID + " )"
      else :
        ruleConjuncts_map[ rid ] = currConjunct_str + " & " + predID
    else :
      if sign :
        ruleConjuncts_map[ rid ] = "~( " + predID + " )"
      else :
        ruleConjuncts_map[ rid ] = predID

  # add parens
  for rid in ruleConjuncts_map :
    conjunct_str = ruleConjuncts_map[ rid ]
    ruleConjuncts_map[ rid ] = "( " + conjunct_str + " )"

  # build positive DNF fmla
  posFmla = None
  for key in ruleConjuncts_map :
    if posFmla :
      posFmla += " | " + ruleConjuncts_map[key]
    else :
      posFmla = ruleConjuncts_map[key]

  # ----------------------------------------------------------- #
  # negate sympy formulas and simplify into DNF

  # negate DNF
  negFmla = "~( " + posFmla + " )"

  print "negFmla = " + negFmla

  # simplify DNF
  simplified_negFmla = sympy.to_dnf( negFmla )

  print "simplified_negFmla = " + str( simplified_negFmla )

  return simplified_negFmla


###################
#  SET NEW RULES  #
###################
# input DNF string
# output array of clauses of conjuncted predicate ID literals
#
# each negated rule spawns 1 or more new rules, depending upon number of disjuncts.
# each clause corresponds to a new rule.
#
def setNewRules( parentName, ruleName, simplified_negFmla, predicateToID_map, cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running set new rules ..."

  #print "simplified_negFmla = " + str( simplified_negFmla ) 
  #tools.dumpAndTerm( cursor )

  # -------------------------------------------------------------------- #
  # initialize local data collection structures                          #
  # -------------------------------------------------------------------- #
  newName       = "not_" + ruleName + "_from_" + parentName
  newGoalAtts   = [] # populate with a uniform set of variables and propogate the set among all DM rules.
  newRIDs       = [] # list of the rids for the new DM rules.
  goalAttMapper = {} # maintain a consistent set of goal attribute strings across all DM rules.

  # -------------------------------------------------------------------- #
  # populate goal attribute mapper with uniform attribute strings.

  # get an rid for this rule
  cursor.execute( "SELECT rid FROM Rule WHERE goalName='" + ruleName + "'" )
  ridList   = cursor.fetchall()
  ridList   = tools.toAscii_list( ridList )
  pickedRID = ridList[0]

  # get original attribute list. This is authoratative b/c
  # setting uniform variable scheme prior to applying DeMorgan's rewrites.
  cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid='" + pickedRID + "'" )
  origAttList = cursor.fetchall()
  origAttList = tools.toAscii_multiList( origAttList )

  # fill goalAttMapper with attID : uniform string
  for att in origAttList :
    attID   = att[0]
    attName = att[1]
    goalAttMapper[ attID ] = attName

  # -------------------------------------------------------------------- #
  # get all clauses for this rule                                        #
  # -------------------------------------------------------------------- #
  negated_simplified_fmla_str = str( simplified_negFmla )
  negated_simplified_fmla_str = negated_simplified_fmla_str.translate( None, string.whitespace)
  negated_simplified_fmla_str = negated_simplified_fmla_str.replace( "(", "" )
  negated_simplified_fmla_str = negated_simplified_fmla_str.replace( ")", "" )
  clauses                     = negated_simplified_fmla_str.split( "|" )

  # -------------------------------------------------------------------- #
  # get predicate (subgoal) ID mapping for this rule                     #
  # predicateToID_map[ predID ] = [ rid, [ sign, sid ] ]                 #
  # -------------------------------------------------------------------- #
  predMap = predicateToID_map

  # -------------------------------------------------------------------- #
  # spawn one new not_ rule per clause                                   #
  # -------------------------------------------------------------------- #
  for c in clauses :

    # get an id for the new rule
    newRID = tools.getID()
    newRIDs.append( newRID )

    # grab the list of literals in this clause
    literalList = c.split( "&" )

    # iterate over literal list to construct the string representation
    for literal in literalList :

      # remove negation from string and record a notin for this subgoal.
      if "~" in literal :
        predicate = literal.replace( "~", "" )
        addArg    = "notin"

      # no negation means do nothing.
      else :
        predicate = literal
        addArg    = None

      # grab the parent rid, sign, and sid for this subgoal
      # represented by this literal in the Boolean formula.
      predData  = predMap[ predicate ]
      rid       = predData[0]
      sign      = predData[1][0]
      sid       = predData[1][1]

      # grab info regarding the original rule.
      origRule             = Rule.Rule( rid, cursor )
      origRule_typeMap     = origRule.getAllAttTypes()
      origRule_goalAttList = origRule.getGoalAttList()

      # -------------------------------------------- #
      # get subgoal info                             #
      # -------------------------------------------- #
      # get name and time arg for this subgoal from the original rule.
      cursor.execute( "SELECT subgoalName,subgoalTimeArg FROM Subgoals WHERE rid='" + rid + "' AND sid='" + sid + "'"  )
      data           = cursor.fetchone()
      data           = tools.toAscii_list( data )
      subgoalName    = data[0]
      try :
        subgoalTimeArg = data[1]
      except IndexError :
        subgoalTimeArg = ""

      #print "here"
      #tools.dumpAndTerm( cursor )

      # get subgoal attribute list
      cursor.execute( "SELECT attID,attName,attType FROM SubgoalAtt WHERE rid='" + rid + "' AND sid='" + sid + "'" )
      subgoalAtts = cursor.fetchall()
      subgoalAtts = tools.toAscii_multiList( subgoalAtts )

      # -------------------------------------------- #
      # save subgoal with the rid of the new rule    #
      # -------------------------------------------- #
      # create new sid
      newSID = tools.getID()

      # save subgoal name and time arg
      cursor.execute( "INSERT INTO Subgoals VALUES ('" + newRID + "','" + newSID + "','" + subgoalName.lower() + "','" + subgoalTimeArg + "')" )

      # save subgoal attributes
      for att in subgoalAtts :
        attID        = att[0]
        attName      = att[1]
        attType      = att[2]
        goalAttNames = [ x[0] for x in newGoalAtts ]

        # ----------------------------------------------------- #
        # check if atts appear in goal atts                     #
        # if so, get the corresponding attID from goal att list #
        # ----------------------------------------------------- #
        goalAttID = None
        if attName in origRule_goalAttList :
          goalAttID = origRule_goalAttList.index( attName )

        # ----------------------------------------------------- #
        if attName == "_" :
          pass

        if not attType == "UNDEFINEDTYPE" and not attName in goalAttNames :
          newGoalAtts.append( [ goalAttID, attName, attType ] )

        elif not attName in goalAttNames :
          if not attType == "UNDEFINEDTYPE" :
            newGoalAtts.append( [ goalAttID, attName, attType ] )
          else :
            attType = origRule_typeMap[ attName ]
            newGoalAtts.append( [ goalAttID, attName, attType ] )

        # replace with uniform goal att str, if applicable
        if not goalAttID == None :
          attName = goalAttMapper[ goalAttID ]

        # insert
        cursor.execute( "INSERT INTO SubgoalAtt VALUES ('" + newRID + "','" + newSID + "','" + str( attID ) + "','" + attName + "','" + attType + "')" )
        #print "completed insert"
        #print "--------------------"
        #print "c = " + str( c )
        #print "origRule : " + dumpers.reconstructRule( rid, cursor )
        #print "subgoalName = " + subgoalName
        #print "subgoalTimeArg = " + subgoalTimeArg
        #print "subgoalAtts = " + str( subgoalAtts )
        #print "origRule_goalAttList = " + str( origRule_goalAttList )
        #print "att = " + str( att )
        #print "goalAttID = " + str( goalAttID )
        #tools.bp( __name__, inspect.stack()[0][3], "breakhere." )

      # save subgoal additional args
      if addArg :
        cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + newRID + "','" + newSID + "','" + str( addArg ) + "')")
      else :
        cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + newRID + "','" + newSID + "','')")


  # -------------------------------------------- #
  # save new goal data

  for newRID in newRIDs :
    # save new goal name and rewritten status
    timeArg       = ""
    rewrittenFlag = True
    cursor.execute( "INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + newRID + "','" + newName + "','" + timeArg + "','" + str(rewrittenFlag) + "')" )

    # save new goal attributes
    #prevInserts = []
    #for attData in newGoalAtts :
    #  goalAttID = attData[0]
    #  attName   = attData[1]
    #  attType   = attData[2]
    #  if not attName == "_" and not goalAttID == None and not goalAttID in prevInserts :
    #    cursor.execute( "INSERT INTO GoalAtt VALUES ('" + newRID + "','" + str(goalAttID) + "','" + goalAttMapper[goalAttID ] + "','" + attType + "')" )
    #    prevInserts.append( goalAttID )

    for attData in origAttList :
      goalAttID = attData[0]
      attName   = attData[1]
      attType   = attData[2]
      cursor.execute( "INSERT INTO GoalAtt VALUES ('" + newRID + "','" + str(goalAttID) + "','" + attName + "','" + attType + "')" )

  # --------------------------------------------------------------------- #

  return newRIDs

#########
#  EOF  #
#########
