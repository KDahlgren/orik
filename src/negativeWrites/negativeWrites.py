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

# ------------------------------------------------------ #

#############
#  GLOBALS  #
#############
NEGATIVEWRITES_DEBUG = tools.getConfig( "DEDT", "NEGATIVEWRITES_DEBUG", bool )

arithOps = [ "+", "-", "*", "/" ]
COUNTER  = 0

#####################
#  NEGATIVE WRITES  #
#####################
def negativeWrites( cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running negative writes ..."

  setNegativeRules( cursor )

  # dump to test
  if NEGATIVEWRITES_DEBUG :
    print
    print "<><><><><><><><><><><><><><><><><><>"
    print ">>> DUMPING FROM negativeWrites <<<"
    print "<><><><><><><><><><><><><><><><><><>"
    dumpers.programDump(  cursor )


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
def setNegativeRules( cursor ) :

  if NEGATIVEWRITES_DEBUG :
    print " ... running set negative rules ..."

  # --------------------------------------------------- #
  # run input program and collect results               #
  # --------------------------------------------------- #

  # get results from running the input program P
  pResults = evaluate( cursor )

  # --------------------------------------------------- #
  # rewrite lines containing negated IDBs               #
  # --------------------------------------------------- #

  # maintian list of IDB goal names to rewrite
  negatedList = []

  pRIDs = getAllRuleRIDs( cursor )

  for rid in pRIDs :
    if ruleContainsNegatedIDB( rid, cursor ) :
      negatedIDBNames = rewriteParentRule( rid, cursor )
      negatedList.extend( negatedIDBNames )
    else :
      pass

  # --------------------------------------------------- #
  # add new rules for negated IDBs                      #
  # --------------------------------------------------- #

  for nameData in negatedList :

    name      = nameData[0]  # name of negated IDB subgoal
    parentRID = nameData[1]  # rid of parent rule

    # collect all rids for this IDB name
    nameRIDs = getRIDsFromName( name, cursor )

    # rewrite original rules to shift function calls in goal atts to eqns in body
    shiftFunctionCalls( nameRIDs, cursor )

    # rewrite original rules with uniform universal attribute variables
    setUniformUniversalAttributes( nameRIDs, cursor )

    # apply the demorgan's rewriting scheme to the rule set.
    applyDeMorgans( parentRID, nameRIDs, cursor )

    dumpers.programDump(  cursor )
    tools.bp( __name__, inspect.stack()[0][3], "blah" )

    # add domain subgoals
    addDomainSubgoals( nameRIDs, cursor )

  # --------------------------------------------------- #
  # final checks
  # --------------------------------------------------- #
  # branch on continued presence of negated IDBs

  # recurse if rewritten program still contains rogue negated IDBs
  if stillContainsNegatedIDBs( cursor ) :
    COUNTER += 1
    negativeWrites( cursor )

  # otherwise, the program only has negated EDB subgoals.
  # return accordingly.
  else :
    return


#########################
#  ADD DOMAIN SUBGOALS  #
#########################
# add domain constraints to universal attributes per rewritten rule.
def addDomainSubgoals( nameRIDs, cursor ) :
  return None


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

  # ------------------------------------------------------- #
  # get arity of this IDB                                   #
  # ------------------------------------------------------- #
  arity = None
  for rid in rids :
    cursor.execute( "SELECT attID FROM GoalAtt WHERE rid=='" + rid + "'" )
    attIDs = cursor.fetchall()
    attIDs = [ a[0] for a in attIDs ]
    ar     = max( attIDs ) + 1
    if arity and not arity == ar :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : schema mismatch in rules :\n" + printRules( rids, curosr ) )
    else :
      arity = ar

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
    if isIDB( subgoalName, cursor ) :
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
def rewriteParentRule( rid, cursor ) :

  negatedIDBNames = []

  # get rule name
  cursor.execute( "SELECT goalName FROM Rule WHERE rid='" + rid + "'" )
  goalName = cursor.fetchone()
  goalName = tools.toAscii_str( goalName[0] )

  # get list of negated IDB subgoals
  cursor.execute( "SELECT Subgoals.sid,Subgoals.subgoalName FROM Subgoals,SubgoalAddArgs WHERE Subgoals.rid='" + rid + "' AND Subgoals.rid==SubgoalAddArgs.rid AND Subgoals.sid==SubgoalAddArgs.sid AND argName=='notin'" )
  negatedSubgoals = cursor.fetchall()
  negatedSubgoals = tools.toAscii_multiList( negatedSubgoals )

  # substitute with appropriate positive counterpart
  for subgoal in negatedSubgoals :
    sid  = subgoal[0]
    name = subgoal[1]

    positiveName = "not_" + name + "_from_" + goalName

    # substitute in positive subgoal name
    cursor.execute( "UPDATE Subgoals SET subgoalName=='" + positiveName + "' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

    # erase negation on this subgoal
    cursor.execute( "UPDATE SubgoalAddArgs SET argName=='' WHERE rid=='" + rid + "' AND sid=='" + sid + "'" )

    # save for return data
    negatedIDBNames.append( [ name, rid ] )

  return negatedIDBNames


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
  deMorgans.doDeMorgans( parentRID, nameRIDs, cursor )


#################################
#  STILL CONTAINS NEGATED IDBS  #
#################################
def stillContainsNegatedIDBs( cursor ) :
  return None


##############
#  EVALUATE  #
##############
def evaluate( cursor ) :

  # translate into c4 datalog
  allProgramLines = c4_translator.c4datalog( cursor )

  # run program
  results_array = c4_evaluator.runC4_wrapper( allProgramLines )

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
  eval_results_dump_to_file( results_array, eval_results_dump_dir )

  # ----------------------------------------------------------------- #
  # parse results into a dictionary
  parsedResults = tools.getEvalResults_dict_c4( results_array )

  # ----------------------------------------------------------------- #

  return parsedResults


###############################
#  EVAL RESULTS DUMP TO FILE  #
###############################
def eval_results_dump_to_file( results_array, eval_results_dump_dir ) :

  eval_results_dump_file_path = eval_results_dump_dir + "eval_dump_" + str( COUNTER ) + ".txt"

  # save new contents
  f = open( eval_results_dump_file_path, "w" )

  for line in results_array :

    # output to stdout
    if NEGATIVEWRITES_DEBUG :
      print line

    # output to file
    f.write( line + "\n" )

  f.close()


#########
#  EOF  #
#########
