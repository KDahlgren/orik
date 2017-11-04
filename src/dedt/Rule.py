#!/usr/bin/env python

'''
Rule.py
   Defines the Rule class.
   Establishes all relevant attributes and get/set methods.
'''

import inspect, os, sqlite3, sys

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from utils import dumpers, extractors, tools
# ------------------------------------------------------ #

DEBUG = tools.getConfig( "DEDT", "RULE_DEBUG", bool )

opList   = [ "notin" ] # TODO: make this configurable
arithOps = [ "+", "-", "*", "/", "==", "!=" ]
intOps   = [ "+", "-", "*", "/" ]
aggOps = [ "min<", "max<", "sum<", "avg<", "count<" ]

class Rule :

  ################
  #  ATTRIBUTES  #
  ################
  rid      = ""
  cursor   = None

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, rid, cursor ) :
    self.rid      = rid
    self.cursor   = cursor

  # ------------------------------------- #
  #                GET                    #
  # ------------------------------------- #

  ###################
  #  GET GOAL NAME  #
  ###################
  def getGoalName( self ) :
    self.cursor.execute( "SELECT goalName FROM Rule WHERE rid = '" + self.rid + "'" )
    nameList = self.cursor.fetchall()
    nameList = tools.toAscii_list( nameList )

    if not nameList == None and not nameList == [] :
      if len(nameList) == 1 :
        return nameList[0]
      else :
        sys.exit( "ERROR: Rule possesses more than one goal : " + nameList )
    else :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : rid does not correspond to a goal." )

  ###################
  #  GET REWRITTEN  #
  ###################
  def getRewritten( self ) :
    self.cursor.execute( "SELECT rewritten FROM Rule WHERE rid = '" + self.rid + "'" )
    rewrittenList = self.cursor.fetchall()
    rewrittenList = tools.toAscii_list( nameList )
    if not rewrittenList == None :
      if len(rewrittenList) == 1 :
        return rewrittenList[0]
      else :
        sys.exit( "ERROR: Rule possesses more than one rewritten flag : " + rewrittenList )

  #############################
  #  GET GOAL ATTRIBUTE LIST  #
  #############################
  def getGoalAttList( self ) :
    self.cursor.execute( "SELECT attName FROM GoalAtt WHERE rid = '" + self.rid + "'" )
    attList = self.cursor.fetchall()
    attList = tools.toAscii_list( attList )
    return attList

  ###########################
  # GET GOAL TIME ARGUMENT  #
  ###########################
  def getGoalTimeArg( self ) :
    self.cursor.execute( "SELECT goalTimeArg FROM Rule WHERE rid = '" + self.rid + "'" )
    timeArgList = self.cursor.fetchall()
    timeArgList = tools.toAscii_list( timeArgList )
    if not timeArgList == None :
      if len(timeArgList) == 1 :
        return timeArgList[0]
      else :
        sys.exit( "ERROR: Rule goal possesses more than 1 time argument : " + timeArgList )

  #############################
  #  GET SUBGOAL LIST STRING  #
  #############################
  # return the body of the rule as a string
  def getSubgoalListStr( self ) :
    self.cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + self.rid + "'" )
    subIDList = self.cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    subgoalList = ""
    currSubgoal = ""

    # iterate over sids
    for k in range(0,len(subIDList)) :
      sid = subIDList[ k ]

      # get subgoal name
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
      subgoalName = self.cursor.fetchone()

      if not subgoalName == None :
        subgoalName = tools.toAscii_str( subgoalName )

        # get subgoal attribute list
        self.cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
        subAtts = self.cursor.fetchall()
        subAtts = tools.toAscii_list( subAtts )

        # get subgoal time arg
        self.cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subTimeArg = self.cursor.fetchone() # assume only one additional arg
        subTimeArg = tools.toAscii_str( subTimeArg )

        ## get subgoal additional args
        self.cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subAddArg = self.cursor.fetchone() # assume only one additional arg
        if not subAddArg == None :
          subAddArg = tools.toAscii_str( subAddArg )

        # all subgoals have a name and open paren
        if not subAddArg == None :
          currSubgoal += subAddArg + " "
        currSubgoal += subgoalName + "("

        # add in all attributes
        for i in range(0,len(subAtts)) :
          if i < (len(subAtts) - 1) :
            currSubgoal += subAtts[i] + ","
          else :
            currSubgoal += subAtts[i] + ")"

        # conclude with time arg, if applicable
        if not subTimeArg == "" :
          currSubgoal += "@" + subTimeArg

        # cap with a comma, if applicable
        if k < len( subIDList ) - 1 :
          currSubgoal += ","

      subgoalList += currSubgoal
      currSubgoal = ""

    return subgoalList


  ######################################################
  #  GET SUBGOAL LIST STRING NO TIME ARGS NO ADD ARGS  #
  ######################################################
  # return the body of the rule as a string sans subgoal time args
  def getSubgoalListStr_noTimeArgs_noAddArgs( self ) :
    self.cursor.execute( "SELECT sid FROM Subgoals WHERE rid = '" + self.rid + "'" )
    subIDList = self.cursor.fetchall()
    subIDList = tools.toAscii_list( subIDList )

    subgoalList = ""
    currSubgoal = ""

    #print "rule: " + dumpers.reconstructRule( self.rid, self.cursor )

    # iterate over sids
    for k in range(0,len(subIDList)) :
      sid = subIDList[ k ]

      # get subgoal name
      self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
      subgoalName = self.cursor.fetchone()

      if not subgoalName == None :
        subgoalName = tools.toAscii_str( subgoalName )

        #print ">>> subgoalName = " + subgoalName

        # get subgoal attribute list
        subAtts = self.cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" )
        subAtts = self.cursor.fetchall()
        subAtts = tools.toAscii_list( subAtts )

        # get subgoal time arg
        self.cursor.execute( "SELECT subgoalTimeArg FROM Subgoals WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subTimeArg = self.cursor.fetchone() # assume only one additional arg
        subTimeArg = tools.toAscii_str( subTimeArg )

        ## get subgoal additional args
        self.cursor.execute( "SELECT argName FROM SubgoalAddArgs WHERE rid == '" + self.rid + "' AND sid == '" + sid + "'" ) # get list of sids for this rule
        subAddArg = self.cursor.fetchone() # assume only one additional arg
        if not subAddArg == None :
          subAddArg = tools.toAscii_str( subAddArg )

        currSubgoal += subgoalName + "("

        # add in all attributes
        for i in range(0,len(subAtts)) :
          if i < (len(subAtts) - 1) :
            currSubgoal += subAtts[i] + ","
          else :
            currSubgoal += subAtts[i] + ")"

        # conclude with time arg, if applicable
        #if not subTimeArg == "" :
        #  currSubgoal += "@" + subTimeArg

        # cap with a comma, if applicable
        if k < len( subIDList ) - 1 :
          currSubgoal += ","

      subgoalList += currSubgoal
      currSubgoal = ""

    return subgoalList


  ##############################
  #  GET EQUATION LIST STRING  #
  ##############################
  def getEquationListStr( self ) :
    self.cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
    eqnIDs = self.cursor.fetchall()
    eqnIDs = tools.toAscii_list( eqnIDs )

    eqnList = ""

    # iterate over equations in rule
    for e in range(0,len(eqnIDs)) :
      currEqnID = eqnIDs[e]

      # get associated equation
      if not currEqnID == None :
        self.cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + self.rid + "' AND eid == '" + str(currEqnID) + "'" )
        eqn = self.cursor.fetchone()
        if not eqn == None :
          eqn = tools.toAscii_str( eqn )

          # convert eqn info to pretty string
          eqnList += eqn
          if not e < len(eqnIDs) :
            eqnList += ","

    return eqnList


  #############################
  #  GET EQUATION LIST ARRAY  #
  #############################
  def getEquationListArray( self ) :
    self.cursor.execute( "SELECT eid FROM Equation" ) # get list of eids for this rule
    eqnIDs = self.cursor.fetchall()
    eqnIDs = tools.toAscii_list( eqnIDs )

    eqnList = []

    # iterate over equations in rule
    for e in range(0,len(eqnIDs)) :
      currEqnID = eqnIDs[e]

      # get associated equation
      if not currEqnID == None :
        self.cursor.execute( "SELECT eqn FROM Equation WHERE rid == '" + self.rid + "' AND eid == '" + str(currEqnID) + "'" )
        eqn = self.cursor.fetchone()
        if not eqn == None :
          eqn = tools.toAscii_str( eqn )

          # convert eqn info to pretty string
          if not e < len(eqnIDs) :
            eqn += ","
          eqnList.append(eqn)

    return eqnList



  # ------------------------------------- #
  #                SET                    #
  # ------------------------------------- #

  ###################
  #  SET GOAL INFO  #
  ###################
  # set goal name and time arg
  def setGoalInfo( self, name, timeArg, rewrittenFlag ) :
    #if timeArg == None :
    #  timeArg = 'async'
    self.cursor.execute("INSERT INTO Rule (rid, goalName, goalTimeArg, rewritten) VALUES ('" + self.rid + "','" + name + "','" + timeArg + "','" + str(rewrittenFlag) + "')")


  #######################
  #  SET GOAL ATT LIST  #
  #######################
  # set goal attribute list
  def setGoalAttList( self, attList ) :
    attID = 0  # allows duplicate attributes in attList
    for attName in attList :
      self.cursor.execute("INSERT INTO GoalAtt VALUES ('" + self.rid + "','" + str(attID) + "','" + attName + "','UNDEFINEDTYPE')")
      attID += 1


  #############################
  #  SET SINGLE SUBGOAL INFO  #
  #############################
  # set single subgoal name and time argument
  def setSingleSubgoalInfo( self, sid, subgoalName, subgoalTimeArg ) :
    # replace any ops with empty
    for op in opList :
      op = "___" + op + "___"
      if op in subgoalName :
        subgoalName = subgoalName.replace( op, "" )

    #if self.getGoalName() == "pre" and subgoalName == "bcast" :
    #  print "my name is pre"
    #  print "subgoalTimeArg = " + str( subgoalTimeArg )
    #  #tools.bp( __name__, inspect.stack()[0][3], "blah" )

    self.cursor.execute("INSERT INTO Subgoals VALUES ('" + self.rid + "','" + sid + "','" + subgoalName + "','" + subgoalTimeArg + "')")


  #################################
  #  SET SINGLE SUBGOAL ATT LIST  #
  #################################
  # set single subgoal attribute list
  def setSingleSubgoalAttList( self, sid, subgoalAttList ) :
    attID = 0 # allows duplicate attributes in list
    for attName in subgoalAttList :
      self.cursor.execute("INSERT INTO SubgoalAtt VALUES ('" + self.rid + "','" + sid + "','" + str(attID) + "','" + attName + "','UNDEFINEDTYPE')")
      attID += 1


  ########################
  #  SET SINGLE SUBGOAL  #
  ########################
  # set single subgoal additional arguments
  def setSingleSubgoalAddArgs( self, sid, subgoalAddArgs ) :
    for addArg in subgoalAddArgs :
      self.cursor.execute("INSERT INTO SubgoalAddArgs VALUES ('" + self.rid + "','" + sid + "','" + addArg + "')")


  ####################
  #  SET SINGLE EQN  #
  ####################
  # set single equation
  def setSingleEqn( self, eid, eqn ) :
    self.cursor.execute("INSERT INTO Equation VALUES ('" + self.rid + "','" + eid + "','" + eqn + "')")


  ###################
  #  SET ATT TYPES  #
  ###################
  # set the types for attributes located within a goal head
  # if goal corresponds to a fact, consult fact data.
  # else goal is an IDB, so gather types recursively.
  def setAttTypes( self ) :
    head_atts      = self.getGoalAttList()
    body_str       = self.getSubgoalListStr_noTimeArgs_noAddArgs()
    allAttTypeMaps = self.allAttTypeMapsDriver( head_atts, body_str )

    #print "thisRule: " + dumpers.reconstructRule( self.rid, self.cursor )
    types = [ allAttTypeMaps[key] for key in allAttTypeMaps ]
    #print "allAttTypeMaps = " + str( allAttTypeMaps )
    #if "UNDEFINEDTYPE" in types :
    #  tools.bp( __name__, inspect.stack()[0][3], "allAttTypeMaps = " + str( allAttTypeMaps ) )

    goalName = self.getGoalName()
    #if "log_log_" in goalName[0:8] and "_log_" in goalName[12:17] :
    #  tools.bp( __name__, inspect.stack()[0][3], "stuff" )

    if DEBUG :
      print "allAttTypeMaps = " + str(allAttTypeMaps) 

    # get all att info
    self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + self.rid + "'" )
    allAtts = self.cursor.fetchall()
    allAtts = tools.toAscii_multiList( allAtts )

    for att in allAtts :
      attID   = att[0]
      attName = att[1]
      attType = allAttTypeMaps[ attName ]

      self.cursor.execute( "UPDATE GoalAtt SET attType=='" + attType + "' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) + " AND attName=='" + attName + "'" )

    # dump table for debugging
    if DEBUG :
      self.cursor.execute( "SELECT * FROM GoalAtt" )
      res = self.cursor.fetchall()
      res = tools.toAscii_multiList( res )
      print "CONTENTS OF TABLE GoalAtt"
      for r in res :
        print r

    return allAttTypeMaps


  #######################
  #  GET ALL ATT TYPES  #
  #######################
  def getAllAttTypes( self ) :
    allAttTypeMaps = self.completeAttTypeMapsDriver()
    return allAttTypeMaps


  ###################################
  #  COMPLETE ATT TYPE MAPS DRIVER  #
  ###################################
  def completeAttTypeMapsDriver( self ) :

    #print "------------------------------------"
    #print " running completeAttTypeMapsDriver "

    completeAttTypeMap = {}

    all_atts              = self.getAllAttList()
    body_str              = self.getSubgoalListStr_noTimeArgs_noAddArgs()
    subgoals_namesAndAtts = self.getInfo_subgoals_namesAndAtts( body_str )

    #print "rule : " + dumpers.reconstructRule( self.rid, self.cursor )

    for att in all_atts :

      #print "att = " + att

      # ------------------------------------- #
      # easy ones
      if "SndTime" in att :
        completeAttTypeMap[ att ] = "int"

      # ------------------------------------- #
      else :
        # ---------------------------------------------------- #
        # list of subgoal names containing the attribute 
        # and index at which the attribute appears.
        candSubs = []

        #print "subgoals_namesAndAtts = " + str( subgoals_namesAndAtts )

        # get list of subs containing the attribute
        for sub in subgoals_namesAndAtts :
          subName  = sub[0]
          sattList = sub[1]

          if att in sattList :
            candSubs.append( [ subName, sattList.index( att ) ] )

        # ---------------------------------------------------- #
        # pick an authoratative sub to use as a starting 
        # point for discovering the type of the current att.
        # prefer facts. if no facts, prefer non-recursive 
        # subgoals. otherwise, pick a recursive subgoal.
        if len( candSubs ) > 0 :

          # =================================================== #
          # bool controlling repeated iterations over candSubs.
          flag_DoNotExit = True

          # =================================================== #
          # prefer facts

          #print "candSubs = " + str( candSubs )

          for sub in candSubs :
            subName  = sub[0]
            subattID = sub[1]

            if tools.isFact( subName, self.cursor ) :
              #print " >> rule = " + dumpers.reconstructRule( self.rid, self.cursor )
              #print "here2"
              completeAttTypeMap[ att ] = self.getFactType( subName, subattID )
              flag_DoNotExit            = False
              break # break out of candSubs loop

          # =================================================== #
          # no facts in rule with the particular attribute 
          # under consideration. pick a non-fact subgoal and recurse.
          if flag_DoNotExit :

            #print "candSubs = " + str( candSubs )

            # find the first subgoal containing the reference to the hatt attribute
            for sub in candSubs :
              currSubName = sub[0]
              currIndex   = sub[1]

              #print "here2: currSubName = " + currSubName,
              #print ", currIndex = " + str( currIndex )
              completeAttTypeMap[ att ] = self.allAttTypeMapsHelper( [ self.rid ], [], currSubName, currIndex )

        # ---------------------------------------------------- #
        # attribute not found in subgoals
        else :

          # check if attribute appears in equation
          self.cursor.execute( "SELECT eqn FROM Equation WHERE rid=='" + self.rid + "'" )
          eqnList = self.cursor.fetchall()
          eqnList = tools.toAscii_list( eqnList )

          flag = False
          for eqn in eqnList :
            if att in eqn :
              flag = True

          # CASE : found att in an eqn
          if flag :
            completeAttTypeMap[ att ] = "int"
            #tools.bp( __name__, inspect.stack()[0][3], "eqnList = " + str( eqnList ) )

          # CASE : direct string input
          elif att.startswith( '"' ) and att.endswith( '"' ) :
            completeAttTypeMap[ att ] = "string"
            #tools.bp( __name__, inspect.stack()[0][3], "sheesh" )

          # CASE : could not find att in any subgoals or eqns for this rule
          else :

            flag = False
            for op in intOps :
              if op in att :
                flag = True
                completeAttTypeMap[ att ] = "int"

            if not flag :
              tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR1 : rule head contains attribute not appearing in any subgoal: \nUnresolved attribute '" + att + "' in the head of rule:\n" + self.display() + "\nAborting..." )

    return completeAttTypeMap


  ######################
  #  GET ALL ATT LIST  #
  ######################
  def getAllAttList( self ) :

    all_atts = []

    # get all goal attributes
    all_atts.extend( self.getGoalAttList() )

    # get all additional atts from subgoals
    self.cursor.execute( "SELECT sid FROM Subgoals WHERE rid='" + self.rid + "'" )
    sidList = self.cursor.fetchall()
    sidList = tools.toAscii_list( sidList )

    for sid in sidList :
      self.cursor.execute( "SELECT attName FROM SubgoalAtt WHERE rid='" + self.rid + "' AND sid='" + sid + "'" )
      attData = self.cursor.fetchall()
      attData = tools.toAscii_list( attData )
      for att in attData :
        if att == "_" :
          pass
        elif not att in all_atts :
          all_atts.append( att )

    return all_atts


  ##############################
  #  ALL ATT TYPE MAPS DRIVER  #
  ##############################
  # input list of head atts and parsed subgoals for current rule.
  # return the type maps for all attribute vars appearing in the body of a rule.
  #
  # for each head att, iterate over subgoal list.
  # if head att appears in subgoal, add subgoal and corresponding 
  # attID to candidate subgoal list.
  # iterate over candidate subgoal list.
  # if any subgoal is a fact, take the attType from one of the facts.
  # else pick record the current rid, pick a non-fact subgoal, and recurse.
  #
  def allAttTypeMapsDriver( self, head_atts, body_str ) :

    print dumpers.reconstructRule( self.rid, self.cursor )

    subgoals_namesAndAtts = self.getInfo_subgoals_namesAndAtts( body_str )

    #if self.getGoalName() == "post" :
    #  print "head_atts             = " + str( head_atts )
    #  print "body_str              = " + str( body_str )
    #  print "subgoals_namesAndAtts = " + str( subgoals_namesAndAtts )

    # iterate over parsed subgoals
    allAttTypeMaps = {}

    for hatt in head_atts :

      #if self.getGoalName() == "post" :
      #  print "hatt = " + hatt

      if "Time" in hatt :
        allAttTypeMaps[ hatt ] = 'int'
        continue

      if DEBUG :
        print "hatt = " + hatt

      # ---------------------------------------------------- #
      # list of subgoal names containing the hatt attribute 
      # and index at which hatt appears.
      candSubs = []

      # get list of subs containing the attribute
      for sub in subgoals_namesAndAtts :
        subName  = sub[0]
        sattList = sub[1]

        if hatt in sattList :
          candSubs.append( [ subName, sattList.index( hatt ) ] )

      # ---------------------------------------------------- #
      # pick an authoratative sub to use as a starting 
      # point for discovering the type of the current att.
      # prefer facts. if no facts, prefer non-recursive 
      # subgoals. otherwise, pick a recursive subgoal.
      if len( candSubs ) > 0 :

        # =================================================== #
        # bool controlling repeated iterations over candSubs.
        flag_DoNotExit = True

        #if self.getGoalName() == "post" :
        #  print "candSubs = " + str( candSubs  )
        #  tools.bp( __name__, inspect.stack()[0][3], "break here." )

        # =================================================== #
        # prefer facts
        for sub in candSubs :
          subName  = sub[0]
          subattID = sub[1]

          print "subName  : " + subName
          print "subattID : " + str( subattID )

          if tools.isFact( subName, self.cursor ) :
            if DEBUG :
              print "subName = " + subName

            #print "here1"
            allAttTypeMaps[ hatt ] = self.getFactType( subName, subattID )
            flag_DoNotExit         = False
            break # break out of candSubs loop

        # =================================================== #
        # no facts in rule with the particular attribute 
        # under consideration. pick a non-fact subgoal and recurse.
        if flag_DoNotExit :

          # find the first subgoal containing the reference to the hatt attribute
          for sub in candSubs :
            currSubName = sub[0]
            currIndex   = sub[1]

            #print "here3."
            goalName = self.getGoalName()
            print "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
            print " FINDING ATT TYPES FOR " + self.getGoalName() 
            print "rule : " + dumpers.reconstructRule( self.rid, self.cursor )

            #if "log_log_" in goalName[0:8] and "_log_" in goalName[12:17] :
            #  print "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
            #  print "rule : " + dumpers.reconstructRule( self.rid, self.cursor )
            #  print " FINDING ATT TYPES FOR " + self.getGoalName() 

            allAttTypeMaps[ hatt ] = self.allAttTypeMapsHelper( [ self.rid ], [], currSubName, currIndex )

            #if "log_log_" in goalName[0:8] and "_log_" in goalName[12:17] :
            #  print " CONCLUSION : allAttTypeMaps[ hatt ] = " + str( allAttTypeMaps[ hatt ] )
            #  print "___________________________________________"

      else :

        # CASE : direct string input in head
        if hatt.startswith( '"' ) and hatt.endswith( '"' ) :
          allAttTypeMaps[ hatt ] = "string"
          #tools.bp( __name__, inspect.stack()[0][3], "sheesh" )
        elif hatt.startswith( "'" ) and hatt.endswith( "'" ) :
          allAttTypeMaps[ hatt ] = "string"
          #tools.bp( __name__, inspect.stack()[0][3], "sheesh" )

        # CASE : direct integer input in head
        elif hatt.isdigit() :
          allAttTypeMaps[ hatt ] = "int"

        # CASE : WTF???
        else :

          # check if att contains an integer operator or contains an aggregate call
          flag = False
          for op in intOps :
            if op in hatt :
              flag = True
              allAttTypeMaps[ hatt ] = "int"
            elif self.isAggregate( hatt )  :
              flag = True
              allAttTypeMaps[ hatt ] = "int"

          if not flag :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR2 : rule head contains attribute not appearing in any subgoal: \nUnresolved attribute '" + hatt + "' in the head of rule:\n" + self.display() + "\nAborting..." )

    return allAttTypeMaps


  ##############################
  #  ALL ATT TYPE MAPS HELPER  #
  ##############################
  # currRIDList        := the list of rule ids under consideration for deriving the type of 
  #                       the targetted goal attribute
  # prospectiveRIDList := the list of rids for IDBs corresponding to subgoals in the original rule
  #                       which define the targeted goal attribute
  # currSubName        := the name of the subgoal currently representing the authority 
  #                       on the type of the targeted attribute
  # currIndex          := the index of the attribute in currSubName from which to derive a type
  def allAttTypeMapsHelper( self, currRIDList, prospectiveRIDList, currSubName, currIndex ) :

    print "//////////////////////////////////////"
    print "currRIDList = " + str( currRIDList )
    print "currSubName = " + str( currSubName )
    print "currIndex   = " + str( currIndex )

    for r in currRIDList :
      print dumpers.reconstructRule( r, self.cursor )

    if DEBUG :
      print "currRIDList = " + str(currRIDList) + "\ncurrSubName = " + str(currSubName) + "\ncurrIndex = " + str(currIndex)

    # --------------------------------------------- #
    # BASE CASE : currSubName is a fact
    # grab data type at index currIndex
    if tools.isFact( currSubName, self.cursor ) :

      print currSubName + " is an EDB!"

      # clock facts are easy
      clockSchema = [ 'string', 'string', 'int', 'int' ]
      if currSubName == "clock" :
        return clockSchema[ currIndex ]

      # grab all fact ids for this fact subgoal
      self.cursor.execute( "SELECT fid FROM Fact WHERE Fact.name=='" + currSubName + "'" )
      fids = self.cursor.fetchall()
      fids = tools.toAscii_list( fids )

      # grab att type for data at given index
      self.cursor.execute( "SELECT attType FROM FactAtt WHERE fid=='" + fids[0] + "' AND attID=='" + str( currIndex ) + "'" )
      attType = self.cursor.fetchone()

      try :
        attType = tools.toAscii_str( attType )
      except TypeError :
        tools.bp( __name__, inspect.stack()[0][3], "shit" )

        attType = "UNDEFINED"

      #self.cursor.execute( "SELECT Fact.fid,name,attID,attName,attType,timeArg FROM Fact,FactAtt WHERE Fact.fid==FactAtt.fid AND Fact.name=='" + currSubName + "'" )
      #res = self.cursor.fetchall()
      #res = tools.toAscii_multiList( res )
      #print ".........................."
      #print "res:"
      #for r in res :
      #  print r
      #print ".........................."

      #print "+"
      #print "+ tools.isFact( " + currSubName + ", self.cursor ) = " + str( tools.isFact( currSubName, self.cursor ) ) 
      #print "+ currSubName = " + currSubName
      #print "+ currIndex   = " + str( currIndex )
      #print "+ attType     = " + attType
      #print "+"

      #if self.getGoalName() == "post" :
      #  print "attType = " + attType

      return attType

    # --------------------------------------------- #
    # RECURSIVE CASE
    else :
      print currSubName + " is an IDB!"

      #print "currSubName = " + currSubName

      #goalName = self.getGoalName()
      #if "log_log_" in goalName[0:8] and "_log_" in goalName[12:17] :
      #  print "currRIDList = " + str( currRIDList )
      #  print "currSubName = " + str( currSubName )
      #  print "currIndex   = " + str( currIndex )
        #tools.bp( __name__, inspect.stack()[0][3], "stuff" )

      # ..................................... #
      # get list of rids for currSubName.
      self.cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + currSubName + "'" )
      allRIDs = self.cursor.fetchall()
      allRIDs = tools.toAscii_list( allRIDs )

      prospectiveRIDList.extend( allRIDs )

      print "allRIDs = " + str( allRIDs ), "currRIDList = " + str( currRIDList ), "prospectiveRIDs = " + str( prospectiveRIDList )

      if DEBUG :
        print "allRIDs = " + str(allRIDs)

      #print "currSubName = " + currSubName
      #print "allRIDs     = " + str( allRIDs )
      #for rid in allRIDs :
      #  print dumpers.reconstructRule( rid, self.cursor )

      # ..................................... #
      # pick rid not previously considered.
      chosenRID = None
      for i in allRIDs :
        if i not in currRIDList :
          chosenRID = i

      if not chosenRID :
        chosenRID = prospectiveRIDList.pop()

      print "++++++"
      print dumpers.reconstructRule( chosenRID, self.cursor )

      # ..................................... #
      # no chosen RID means cannot resolve the attribute to a fact component.
      if not chosenRID :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : Cannot resolve to facts : " + self.display() )

      # ..................................... #
      # recurse over the new rid
      currRIDList.append( chosenRID )
      newSubName = None
      newIndex   = None

      # ..................................... #
      # get string of target attribute in new rule
      self.cursor.execute( "SELECT attName FROM GoalAtt WHERE rid = '" + chosenRID + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_list( attList )
      attStr  = attList[ currIndex ]

      #print "attStr = " + attStr
      attStr = self.cleanAttStr( attStr )

      # ..................................... #
      # check if att str is actually data
      print "<><> attStr : " + attStr
      if attStr.startswith( '"' ) and attStr.endswith( '"' ) :
        return "string"

      elif attStr.isdigit() :
        return "int"

      # ..................................... #
      # check if att str is actually an aggregate
      elif self.isAggregate( attStr ) :
        return "int"

      # ..................................... #
      # get first subgoal of chosen rule referencing the target attribute
      self.cursor.execute( "SELECT subgoalName,attID FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + chosenRID + "' AND Subgoals.rid==SubgoalAtt.rid AND Subgoals.sid==SubgoalAtt.sid AND attName=='" + attStr + "'" )
      info = self.cursor.fetchall()
      info = tools.toAscii_multiList( info )

      #print "info = " + str( info )

      # ..................................... #
      # if att doesn't appear in subgoal att list, then check equations
      if info == [] :
        self.cursor.execute( "SELECT eqn FROM Equation WHERE rid='" + chosenRID + "'" )
        eqnList = self.cursor.fetchall()
        eqnList = tools.toAscii_list( eqnList )

        #print "eqnList = " + str( eqnList )

        # ..................................... #
        # find eqn with relelvant att
        for eqn_str in eqnList :
          #print "eqn_str = " + eqn_str
          for op in arithOps :
            #print "op = " + op
            if op in eqn_str :
              eqn = eqn_str.split( op )
              rhs = eqn[0]
              lhs = eqn[1]
              if rhs == attStr :
                if tools.isString( lhs ) :
                  return "string"
                else :
                  return "int"
                #elif tools.isInt( lhs ) :
                #  return "int"
                #else :
                #  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unrecognized data type in lhs '" + str( lhs ) + "' of eqn : " + eqn_str + " in rule " + dumpers.reconstructRule( chosenRID, self.cursor ) )

      print "goalName    = " + self.getGoalName()
      print "currRIDLIST = " + str( currRIDList )
      print "currSubName = " + currSubName
      print "currIndex   = " + str( currIndex )
      print "attStr      = " + str( attStr    )
      print "chosenRID   = " + str( chosenRID )
      print "info        = " + str( info )
      print "++++++"

      targetSub  = info[0]
      newSubName = targetSub[0]
      newIndex   = targetSub[1]

      #print "> targetSub  = " + str( targetSub )
      #print "> newSubName = " + str( newSubName )
      #print "> newIndex   = " + str( newIndex )

      #print "here1."
      return self.allAttTypeMapsHelper( currRIDList, prospectiveRIDList, newSubName, newIndex )


  ##################
  #  IS AGGREGATE  #
  ##################
  # check if the input string contains one of the aggregate operators.
  def isAggregate( self, attStr ) :
    for op in aggOps :
      if op in attStr :
        return True
    return False


  ###################
  #  CLEAN ATT STR  #
  ###################
  def cleanAttStr( self, attStr ) :

    for op in arithOps :
      if op in attStr :
        expr = attStr.split( op )
        lhs_expr = expr[0]
        return lhs_expr

    return attStr


  ###################
  #  GET FACT TYPE  #
  ###################
  def getFactType( self, factName, attID ) :

    print "factName = " + factName
    print "attID    = " + str( attID )

    # ....................................... #
    # clock is easy
    if factName == "clock" :
      typeList = [ 'string', 'string', 'int', 'int' ]
      return typeList[ attID ]

    # ....................................... #
    # crash is easy
    if factName == "crash" :
      typeList = [ 'string', 'string', 'int' ]
      return typeList[ attID ]

    # ....................................... #
    # grab all data types for this fact name
    # at the given attribute ID
    self.cursor.execute( "SELECT attType FROM Fact,FactAtt WHERE name=='" + factName + "' and attID=='" + str(attID) + "' AND Fact.fid==FactAtt.fid" )
    typeList = self.cursor.fetchall()
    typeList = tools.toAscii_list( typeList )

    print "typeList = " + str( typeList )

    # ...................................... #
    # sanity check
    # make sure all types are identical
    for t1 in typeList :
      for t2 in typeList :
        if not t1 == t2 :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : data types not uniform for fact declarations of name '" + factName + "' along index attID = " + str(attID) + "\n typeList = " + str(typeList) )

    # ....................................... #
    if len( typeList ) == 0 :
      tools.bp( __name__, inspect.stack()[0][3], "factName = " + factName + ", attID = " + str( attID ) )

    return typeList[0]


  ##################
  #  GET TYPE MAP  #
  ##################
  # return a list of [ attribute name, attribute type ] maps in the form of arrays
  def getTypeMap( self, subNameAndAtts ) :
    subname = subNameAndAtts[0]
    subatts = subNameAndAtts[1]

    #tools.bp( __name__, inspect.stack()[0][3], "subNameAndAtts = " + str( subNameAndAtts ) )

    atts_inRuleBody = subatts

    if DEBUG :
      print "subNameAndAtts = " + str(subNameAndAtts)

    # --------------------------------------------------- #
    #     BASE CASE 1 !!! => subgoal references a fact
    # --------------------------------------------------- #
    if tools.isFact( subname, self.cursor ) :
      list_dataTypes_fromFact = self.getFactDataTypes( subname )
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, list_dataTypes_fromFact )

    # --------------------------------------------------- #
    #     BASE CASE 2 !!! => subgoal references a fact
    # --------------------------------------------------- #
    elif subname == 'clock' :
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, [ 'string', 'string', 'int', 'int' ] )

    # --------------------------------------------------- #
    #     BASE CASE 3 !!! => subgoal references a fact
    # --------------------------------------------------- #
    elif subname == 'crash' :
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, [ 'string', 'string', 'int' ] )

    # --------------------------------------------------- #
    #     RECURSIVE CASE !!! => subgoal is an idb
    # --------------------------------------------------- #
    else :
      sub_as_rule     = self.getRuleHeadAtts( subname )

      if DEBUG :
        print "subname     = " + str(subname)
        print "subatts     = " + str(subatts)
        print "sub_as_rule = " + str(sub_as_rule)

      chosen_rid      = sub_as_rule[0]
      atts_asRuleHead = sub_as_rule[1]

      subRule                 = Rule( chosen_rid, self.cursor )
      bodyparse               = subRule.getSubgoalListStr_noTimeArgs_noAddArgs()
      allAttTypeMaps          = self.allAttTypeMapsDriver( bodyparse )
      atts_asRuleHead_typeMap = self.mapTypes_preprocessed( atts_asRuleHead, allAttTypeMaps )

      if DEBUG :
        print "subRule                 = " + str(subRule)
        print "bodyparse               = " + str(bodyparse)
        print "allAttTypeMaps          = " + str(allAttTypeMaps)
        print "atts_asRuleHead_typeMap = " + str(atts_asRuleHead_typeMap)

      # following statement only works if atts_asRuleHead_types maintains ordering!!!
      orderedListOfTypes = [ mapping[1] for mapping in atts_asRuleHead_typeMap]

      if DEBUG :
        print "orderedListOfTypes = " + str(orderedListOfTypes)

      #tools.bp( __name__, inspect.stack()[0][3], "orderedListOfTypes = " + str(orderedListOfTypes) + "\natts_asRuleHead_typeMap = " + str(atts_asRuleHead_typeMap) )
      atts_inRuleBody_typeMap = self.mapTypes_raw( atts_inRuleBody, orderedListOfTypes )

      if DEBUG :
        print "atts_inRuleBody_typeMap = " + str(atts_inRuleBody_typeMap)

    #tools.bp( __name__, inspect.stack()[0][3], "atts_inRuleBody_typeMap = " + str(atts_inRuleBody_typeMap) )
    return atts_inRuleBody_typeMap


  ############################
  #  MAP TYPES PREPROCESSED  #
  ############################
  # map attribute vars to types based on ordering.
  # only use for subgoals referencing facts.
  def mapTypes_preprocessed( self, attList, typeMapList ) :

    attList = [ att[1] for att in attList ] # remove attIDs

    # check sanity : attributes defined across type maps should have the same type.
    attDict = {}
    for mappingList in typeMapList :
      for mapping in mappingList :
        att = mapping[0]
        val = mapping[1]

        if att in attDict.keys() :
          if attDict[att] == val :
            pass
          else :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : inconsistent type assignments for attribute " + str(att) + "\n" + str(attDict[att]) + " is not the same as " + str(val) )
        else :
          attDict[att] = val

    # otherwise ... 
    finalMapping = []
    for att in attList : # maintains ordering!!!!
      #print "att          = " + str(att)
      #print "attDict[att] = " + str( attDict[att] )
      finalMapping.append( [ att, attDict[att] ] )

    return finalMapping


  ###################
  #  MAP TYPES RAW  #
  ###################
  # map attribute vars to types based on ordering.
  # only use for subgoals referencing facts.
  def mapTypes_raw( self, attList, orderedListOfTypes ) :

    # check sanity : arity of the facts should equal the arity of the referencing sub rule
    if len(attList) > len(orderedListOfTypes) :
      tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : more attribute variables than data types:\natt vars = " + str(attList) + "\ndata types = " + str(orderedListOfTypes) )

    # fewer atts may occur if subgoal appears in a rule without the time argument.
    # accordingly, because the reference to the subgoal is written without reference to 
    # the time argument, it is ok to just take the first N data types from the ordered type list,
    # where N is the arity of the subgoal reference.
    #elif len(attList) < len(orderedListOfTypes) :
    #  tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : fewer attribute variables than data types:\natt vars = " + str(attList) + "\ndata types = " + str(orderedListOfTypes)  )

    # otherwise ... 
    finalMapping = []
    for i in range(0,len(attList)) :
      finalMapping.append( [ attList[i], orderedListOfTypes[i] ] )

    return finalMapping


  #########################
  #  GET FACT DATA TYPES  #
  #########################
  # return an array containing an ordered list of the data types of
  # all components included in a fact
  def getFactDataTypes( self, subname ) :

    if subname == "clock" :
      return [ 'string', 'string', 'int', 'int' ]

    # retrieve all facts assocaited with the subname
    self.cursor.execute( "SELECT fid FROM Fact WHERE name=='" + subname + "'" )
    allFIDs = self.cursor.fetchall()
    allFIDs = tools.toAscii_list( allFIDs )

    factData_all = []
    for fid in allFIDs :

      # get timing data
      self.cursor.execute( "SELECT timeArg FROM Fact WHERE fid=='" + fid + "'" )
      timeData = self.cursor.fetchone()
      timeData = tools.toAscii_str( timeData )
      if not timeData.isdigit() :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : timeing argument for a " + subname + " fact is not an integer:\n" + timeData + " is not an integer. =["  )

      # get input data
      self.cursor.execute( "SELECT attID,attName FROM FactAtt WHERE fid=='" + fid + "'" )
      factData = self.cursor.fetchall()
      factData = tools.toAscii_multiList( factData )

      # create and save full fact
      fullFact = [ data[1] for data in factData ]
      fullFact.append( timeData )
      factData_all.append( fullFact )

    if DEBUG :
      print "subname = " + subname,
      print "factData_all = " + str(factData_all)

    # pass 1: collect data type lists per fact record.
    factTypesList = []
    for data in factData_all :
      typeList = []
      for component in data :
        if ("'" in component) or ('"' in component) : # check if string
          typeList.append( 'string' )
        elif component.isdigit() :                    # check if int
          typeList.append( 'int' )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR:\nencountered data of unrecognized type :\n data record " + data + "\n for table " + subname + " contains unregognized component " + str(component) + ". pyLDFI currently only supports strings and integers.\nDouble or single quotes must encapsulate the contents of a string.." )
      factTypesList.append( typeList )

    # pass 2: terminate if any type lists are inconsistent.
    for typeList1 in factTypesList :
      for typeList2 in factTypesList :
        for i in range(0,len(typeList)) :
          if typeList1[i] == typeList2[i] :
            pass
          else :
            tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR: type inconsistency in facts for table " + subname + "\n" + typeList1[i] + " does not equal " + typeList2[i]  )

    #tools.bp( __name__, inspect.stack()[0][3], "factTypesList = " + str(factTypesList) )
    return factTypesList[0]


  ########################
  #  GET RULE HEAD ATTS  #
  ########################
  # return a binary array containing the chosen rid for the subgoal rule
  # and the list of all attribute var names used in the goal/head of that
  # particular rule definition.
  def getRuleHeadAtts( self, subname ) :

    allRIDs = self.getAllRIDs( subname )

    subList = []
    for rid in allRIDs :
      sublist = self.getSubList_namesOnly( rid )

      if not subname in subList :
        return [ rid, self.getHeadAtts( rid ) ]


  ##################
  #  GET ALL RIDS  #
  ##################
  # return the complete list of rids associated with the given subgoal name.
  def getAllRIDs( self, subname ) :

    self.cursor.execute( "SELECT rid FROM Rule WHERE goalName=='" + subname + "'" )
    allRIDs = self.cursor.fetchall()
    allRIDs = tools.toAscii_list( allRIDs )

    return allRIDs


  #############################
  #  GET SUB LIST NAMES ONLY  #
  #############################
  # return an array of the subgoal names contained within the given rule.
  def getSubList_namesOnly( self, rid ) :

    self.cursor.execute( "SELECT subgoalName FROM Subgoals WHERE rid=='" + rid + "'" )
    subList_namesOnly = self.cursor.fetchall()
    subList_namesOnly = tools.toAscii_list( subList_namesOnly )

    return subList_namesOnly


  ###################
  #  GET HEAD ATTS  #
  ###################
  # return an array of the goal attribues for the given rule.
  def getHeadAtts( self, rid ) :

    self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + rid + "'" )
    headAtts = self.cursor.fetchall()
    headAtts = tools.toAscii_multiList( headAtts )

    return headAtts


  ######################################
  #  GET INFO SUBGOALS NAMES AND ATTS  #
  ######################################
  # for a given rule body string, return an array of binary arrays
  # st the binary arrays contain a subgoal name and an array of the corresponding
  # attribute variable strings.
  def getInfo_subgoals_namesAndAtts( self, body_str_no_time_args ) :
    subsAndAtts = body_str_no_time_args.split( ")," )

    #print "body_str_no_time_args = " + body_str_no_time_args

    # remove parens and commas
    temp_list = []
    for sub in subsAndAtts :
      temp_sub = ""
      for c in sub :
        if c == "(" :
          temp_sub += "___STARTHERE___"
        elif c == "," :
          temp_sub += "___COMMAHERE___"
        elif c == ")" :
          pass
        else :
          temp_sub += c
      temp_list.append( temp_sub )

    # convert into binary arrays containing subname and parsed array of sub atts.
    temp_list_2 = []
    for sub in temp_list :
      temp_sub       = sub.split( "___STARTHERE___" )
      subname        = temp_sub[0]
      subAttList_str = temp_sub[1]
      subAttList     = subAttList_str.split( "___COMMAHERE___" )
      temp_list_2.append( [ subname, subAttList ] )
    subNamesAndAtts = temp_list_2

    return subNamesAndAtts


  ##############
  #  GET TYPE  #
  ##############
  # comp := lhs or rhs of an equation extracted from a rule
  def getType( self, comp ) :

    # check if constant string
    if ("'" in comp) or ('"' in comp) :
      return "string"

    # check if constant integer
    elif comp.isdigit() :
      return "int"

    # get type from rule definition
    else :
      # check goal att types
      self.cursor.execute( "SELECT attID,attName,attType FROM GoalAtt WHERE rid=='" + self.rid + "'" )
      attInfo_goal = self.cursor.fetchall()
      attInfo_goal = tools.toAscii_multiList( attInfo_goal )

      goalTypeMap = {}
      for att in attInfo_goal :
        attID   = att[0]
        attName = att[1]
        attType = att[2]
        goalTypeMap[ attName ] = attType

      # iterate over subgoals
      self.cursor.execute( "SELECT SubgoalAtt.sid,attID,attName,attType FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid + "' AND Subgoals.rid==SubgoalAtt.rid" )
      attInfo = self.cursor.fetchall()
      attInfo = tools.toAscii_multiList( attInfo )

      for att in attInfo :
        sid     = att[0]
        attID   = att[1]
        attName = att[2]
        attType = att[3]

        # sanity check : the types of the goal atts must correspond to the types in the corresponding subgoalatts
        if (not attName == "_") and (not attType == goalTypeMap[ attName ]) :
          # get goal type dump
          self.cursor.execute( "SELECT Rule.rid,goalName,attID,attName,attType FROM Rule,GoalAtt WHERE Rule.rid=='" + self.rid+ "' AND Rule.rid==GoalAtt.rid" )
          goalTypeDump = self.cursor.fetchall()
          goalTypeDump = tools.toAscii_multiList( goalTypeDump )

          # get subgoal type dump
          self.cursor.execute( "SELECT Subgoals.rid,Subgoals.sid,subgoalName,attID,attName,attType FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid+ "' AND Subgoals.rid==SubgoalAtt.rid" )
          subgoalTypeDump = self.cursor.fetchall()
          subgoalTypeDump = tools.toAscii_multiList( subgoalTypeDump )

          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : Type inconsistency between goal and subgoal attribute type declarations: \nIn rule " + dumpers.reconstructRule( self.rid, self.cursor ) + ",\nattribute '" + attName + "' is of type '" + goalTypeMap[ attName ] + " in the goal, but is of type '" + attType + "' in one of the subgoals.\ngoalTypeDump:\n(rid,goalName,attID,attName,attType)\n" + "\n".join([ str(item) for item in goalTypeDump ]) + "\nsubgoalTypeDump:\n(rid,sid,subgoalName,attID,attName,attType)\n" + "\n".join([ str(item) for item in subgoalTypeDump ])  )

        if comp == attName :
          #print "attName = " + attName + ", attType = " + attType
          return attType

    tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : component '" + comp + "' of equation detected in rule '" + dumpers.reconstructRule( self.rid, self.cursor ) + "' has no detected type." )


  #######################
  #  PROMOTE COMPONENT  #
  #######################
  # promote the type of a component derived from an equation extracted from a string
  # to a more general data type.
  # observe the code will never attempt to promote a string
  def promoteComponent( self, lhs, op, rhs, eid, cat ) :

    tools.bp( __name__, inspect.stack()[0][3], "hit promoteComponent" )

    # =============================================== #
    # handle lhs case 
    # promote integer constants to string
    if lhs.isdigit() :
      newEqn = str(lhs) + op + rhs
      self.cursor.execute( "UPDATE Equation SET eqn=='" + newEqn + "' WHERE rid=='" + rid + "' AND eid=='" + eid + "'" )

    else :
      # promote attributes in original rules to strings
      # reset original goal atts
      self.cursor.execute( "SELECT attID,attName FROM GoalAtt WHERE rid=='" + self.rid + "'" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      for att in attList :
        attID   = att[0]
        attName = att[1]

        if cat == "lhs" :
          if lhs == attName :
            self.cursor.execute( "UPDATE GoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )
        elif cat == "rhs" :
          if rhs == attName :
            self.cursor.execute( "UPDATE GoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND attID==" + str(attID) )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : cat is not lhs or rhs. cat = " + str(cat) + "\nUnrecognized option. Aborting..." )

      # reset original subgoal atts
      self.cursor.execute( "SELECT SubgoalAtt.sid,attID,attName FROM Subgoals,SubgoalAtt WHERE Subgoals.rid=='" + self.rid + "' AND Subgoals.rid==SubgoalAtt.rid" )
      attList = self.cursor.fetchall()
      attList = tools.toAscii_multiList( attList )

      for att in attList :
        sid     = att[0]
        attID   = att[1]
        attName = att[2]

        if cat == "lhs" :
          if lhs == attName :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )
        elif cat == "rhs" :
          if rhs == attName :
            self.cursor.execute( "UPDATE SubgoalAtt SET attType=='string' WHERE rid=='" + self.rid + "' AND sid=='" + sid + "' AND attID==" + str(attID) )
        else :
          tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : cat is not lhs or rhs. cat = " + str(cat) + "\nUnrecognized option. Aborting..." )

    return None


  # ------------------------------------- #
  #              DISPLAY                  #
  # ------------------------------------- #

  #############
  #  DISPLAY  #
  #############
  # print rule to stdout
  def display( self ) :
    prettyRule = ""

    # collect goal info
    goalName = self.getGoalName()
    goalAttList  = self.getGoalAttList()
    goalTimeArg  = self.getGoalTimeArg()

    goalAttStr = ""
    for i in range(0,len(goalAttList)) :
      goalAttStr += goalAttList[i]
      if i < len(goalAttList) - 1 :
        goalAttStr += ","

    # collect subgoal list
    subgoalStr = self.getSubgoalListStr()

    # collect equantion list
    eqnStr = self.getEquationListStr()

    # convert rule info to pretty string
    prettyRule += goalName + "(" + goalAttStr + ")" + " :- " + subgoalStr 
    if eqnStr :
      prettyRule += "," + eqnStr
    prettyRule += " ;"

    #print prettyRule

    return prettyRule

#########
#  EOF  #
#########
