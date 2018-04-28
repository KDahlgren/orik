#!/usr/bin/env python

'''
Test_derivation.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import copy, inspect, logging, os, sqlite3, sys, time, unittest

# ------------------------------------------------------ #
# import sibling packages HERE!!!

if not os.path.abspath( __file__ + "/../../src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../src" ) )

from derivation import FactNode, GoalNode, Node, ProvTree, RuleNode

if not os.path.abspath( __file__ + "/../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../lib/iapyx/src" ) )

from dedt       import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils      import dumpers, globalCounters, tools
from evaluators import c4_evaluator

# ------------------------------------------------------ #


###################################
#  TEST DERIVATION FUNCTIONALITY  #
###################################
class Test_derivation_functionality( unittest.TestCase ) :

  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  PRINT_STOP = False

  ################################
  #  FACT NODE CREATION ERROR 2  #
  ################################
  # test error on the creation of a fact node.
  # error because input name does not reference a fact.
  #@unittest.skip( "working on different example" )
  def test_fact_node_creation_error_2( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )


    # --------------------------------------------------------------- #
    # define data

    name          = "sub0"
    record        = ['b']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    try :
      new_fact_node = FactNode.FactNode( name          = name, \
                                         record        = record, \
                                         parsedResults = parsedResults, \
                                         cursor        = cursor )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.FactNode at function __init__ :\n>>>   FATAL ERROR : relation 'sub0' does not reference a fact. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ################################
  #  FACT NODE CREATION ERROR 1  #
  ################################
  # test error on the creation of a fact node.
  # error because input name does not reference a fact.
  #@unittest.skip( "working on different example" )
  def test_fact_node_creation_error_1( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )


    # --------------------------------------------------------------- #
    # define data

    name          = "sub3"
    record        = ['a']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    try :
      new_fact_node = FactNode.FactNode( name          = name, \
                                         record        = record, \
                                         parsedResults = parsedResults, \
                                         cursor        = cursor )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.FactNode at function __init__ :\n>>>   FATAL ERROR : relation 'sub3' does not reference a fact. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ########################
  #  FACT NODE CREATION  #
  ########################
  # test the creation of a fact node.
  #@unittest.skip( "working on different example" )
  def test_fact_node_creation( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )


    # --------------------------------------------------------------- #
    # define data

    name          = "sub0"
    record        = ['a']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    new_fact_node = FactNode.FactNode( name          = name, \
                                       record        = record, \
                                       parsedResults = parsedResults, \
                                       cursor        = cursor )

    # --------------------------------------------------------------- #
    # tests

    # test __str__
    self.assertTrue( new_fact_node.__str__() == "fact->sub0(['a'])" )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  ################################
  #  RULE NODE CREATION ERROR 2  #
  ################################
  # test error in rule node creation
  # goal is neither edb nor idb
  #@unittest.skip( "working on different example" )
  def test_rule_node_creation_error_2( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('4','sub1','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','0','a','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','1','b','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','2','c','string')" )


    # --------------------------------------------------------------- #
    # define data

    rid           = "1"
    name          = "TestNode_prov0"
    record        = ['a','b','c']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ], \
                      "sub2"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    try :
      new_rule_node = RuleNode.RuleNode( rid           = rid, \
                                         name          = name, \
                                         record        = record, \
                                         parsedResults = parsedResults, \
                                         cursor        = cursor )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.RuleNode at function generate_descendant_meta :\n>>>   FATAL ERROR : subgoal 'sub2' is neither edb nor idb. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ################################
  #  RULE NODE CREATION ERROR 1  #
  ################################
  # test error in rule node creation
  # goal is both edb and idb
  #@unittest.skip( "working on different example" )
  def test_rule_node_creation_error_1( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('4','sub1','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','0','a','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','1','b','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','2','c','string')" )


    # --------------------------------------------------------------- #
    # define data

    rid           = "1"
    name          = "TestNode_prov0"
    record        = ['a','b','c']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    try :
      new_rule_node = RuleNode.RuleNode( rid           = rid, \
                                         name          = name, \
                                         record        = record, \
                                         parsedResults = parsedResults, \
                                         cursor        = cursor )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.RuleNode at function generate_descendant_meta :\n>>>   FATAL ERROR : subgoal 'sub1' is both edb and idb. ambiguous. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ########################
  #  RULE NODE CREATION  #
  ########################
  # test the creation of a rule node with descendants
  #@unittest.skip( "working on different example" )
  def test_rule_node_creation( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','2','_','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','2','_','string')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','2','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','2','0','Z','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','a','string')" )


    # --------------------------------------------------------------- #
    # define data

    rid           = "1"
    name          = "TestNode_prov0"
    record        = ['a','b','c']
    parsedResults = { "TestNode"       : [ ["a","b"] ], \
                      "TestNode_prov0" : [ ["a","b","c"], ["a","b","d"] ], \
                      "sub0"           : [ ["a"] ], \
                      "sub1"           : [ ["b","c","e"], ["b","c","f"], ["b","d","e"] ]  }

    # --------------------------------------------------------------- #
    # create node

    argDict = {}
    argDict[ "settings" ] = "./settings_files/settings.ini"

    new_rule_node = RuleNode.RuleNode( rid           = rid, \
                                       name          = name, \
                                       record        = record, \
                                       parsedResults = parsedResults, \
                                       cursor        = cursor, \
                                       argDict       = argDict )

    # --------------------------------------------------------------- #
    # tests

    # test __str__
    self.assertTrue( new_rule_node.__str__() == "rule->TestNode_prov0(['a', 'b', 'c'])" )

    # test get_trigger_record_for_subgoal
    gatt_to_data = { "X" : "a", "Y" : "b", "Z" : "c" }
    satt_list_1  = [ [0,"X"] ]
    satt_list_2  = [ [0,"Y"], [1,"Z"], [2,"_"] ]
    self.assertTrue( new_rule_node.get_trigger_record_for_subgoal( gatt_to_data, satt_list_1 ) == [ "a" ] )
    self.assertTrue( new_rule_node.get_trigger_record_for_subgoal( gatt_to_data, satt_list_2 ) == [ "b", "c", "_" ] )

    # test check_subgoal_type
    self.assertTrue( new_rule_node.check_subgoal_type( "sub0" ) == [ True, False ] ) # edb
    self.assertTrue( new_rule_node.check_subgoal_type( "sub1" ) == [ False, True ] ) # idb

    # test generate_descendant_meta
    self.assertTrue( new_rule_node.descendant_meta == [ {'treeType': 'goal', \
                                                         'polarity': '', \
                                                         'triggerRecord': ['b', 'c', '_'], \
                                                         'node_name': 'sub1'},
                                                        {'treeType': 'fact', \
                                                         'polarity': '', \
                                                         'triggerRecord': ['a'], \
                                                         'node_name': 'sub0'} ] )


    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  ################################
  #  GOAL NODE CREATION ERROR 1  #
  ################################
  # test failure when attempting to create a goal node such that
  # the corresponding rule has no provenance rules.
  #@unittest.skip( "working on different example" )
  def test_goal_node_creation_error_1( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )

    # --------------------------------------------------------------- #
    # define data

    name          = "TestNode"
    isNeg         = False
    record        = ['a','b']
    parsedResults = { "TestNode" : [ ['a','b'] ] }

    # --------------------------------------------------------------- #

    try :
      new_goal_node = GoalNode.GoalNode( name          = name, \
                                         isNeg         = isNeg, \
                                         record        = record, \
                                         parsedResults = parsedResults, \
                                         cursor        = cursor )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.GoalNode at function get_prov_rid_and_name_list :\n>>>   FATAL ERROR : no provenance rules for 'TestNode'"

    self.assertEqual( actual_error, expected_error )  

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ########################
  #  GOAL NODE CREATION  #
  ########################
  # test the creation of a positive goal node with descendants
  #@unittest.skip( "working on different example" )
  def test_goal_node_creation( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #
    # populate database

    # original rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','TestNode','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Z','string')" )

    # provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','TestNode_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Z','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Z','string')" )

    # --------------------------------------------------------------- #
    # define data

    name          = "TestNode"
    isNeg         = False
    record        = ['a','b']
    parsedResults = { "TestNode" : [ ['a','b'] ], "TestNode_prov0" : [ ['a','b','c'], ['a','b','d'] ]  }

    # --------------------------------------------------------------- #
    # create node

    new_goal_node = GoalNode.GoalNode( name          = name, \
                                       isNeg         = isNeg, \
                                       record        = record, \
                                       parsedResults = parsedResults, \
                                       cursor        = cursor )

    # --------------------------------------------------------------- #
    # tests

    # test __str__
    self.assertTrue( new_goal_node.__str__() == "goal->TestNode(['a', 'b'])" )

    # test get_prov_rid_and_name_list
    self.assertTrue( new_goal_node.get_prov_rid_and_name_list() == [ ['1', 'TestNode_prov0'] ] )

    # test get_valid_prov_records
    self.assertTrue( new_goal_node.get_valid_prov_records( "TestNode_prov0" ) == [ ['a', 'b', 'c'], ['a','b','d'] ] )

    # test generate_descendant_meta
    self.assertTrue( new_goal_node.descendant_meta == {'1': {'goalName'    : 'TestNode_prov0', \
                                                             'triggerData' : [['a', 'b', 'c'],['a','b','d']]}} )


    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  ##################################
  #  EMPTY PROV TREE ERROR CASE 2  #
  ##################################
  # test error case when generating a ProvTree
  # no post records for given eot
  #@unittest.skip( "working on different example" )
  def test_empty_prov_tree_error_case_2( self ) :

    if not os.path.exists( "./data/" ) :
      os.system( "mkdir ./data/" )

    rootname      = "__KD__TESTNODE__KD__"
    parsedResults = { "table1":[ ['a','b'],  ] }
    cursor        = None
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 0
    parent        = None

    # --------------------------------------------------------------- #

    try :
      new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                    parsedResults = parsedResults, \
                                    treeType      = treeType, \
                                    isNeg         = isNeg )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.ProvTree at function generate_tree :\n>>>   GENERATE TREE : FATAL ERROR : no eot post records. aborting."

    self.assertEqual( actual_error, expected_error )


  ##################################
  #  EMPTY PROV TREE ERROR CASE 1  #
  ##################################
  # test error case when generating a ProvTree
  # trying to create a goal node, but no records exist for the goal/relation name
  #@unittest.skip( "working on different example" )
  def test_empty_prov_tree_error_case_1( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    if not os.path.exists( "./data/" ) :
      os.system( "mkdir ./data/" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    rootname      = "__KD__TESTNODE__KD__1"
    parsedResults = { "__KD__TESTNODE__KD__1":[ ['a','b'] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 0
    parent        = None

    # --------------------------------------------------------------- #

    try :
      new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                    parsedResults = parsedResults, \
                                    treeType      = treeType, \
                                    cursor        = cursor, \
                                    isNeg         = isNeg )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.GoalNode at function get_prov_rid_and_name_list :\n>>>   FATAL ERROR : no provenance rules for '__KD__TESTNODE__KD__1'"

    self.assertEqual( actual_error, expected_error )


  ##########################
  #  PROVTREE CONSTRUCTOR  #
  ##########################
  # test construction of smallest possible ProvTree
  #@unittest.skip( "working on different example" )
  def test_prov_tree_constructor( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    if not os.path.exists( "./data/" ) :
      os.system( "mkdir ./data/" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #

    argDict = self.getArgDict( "" )

    rootname      = "__TestNode__"
    parsedResults = { "__TestNode__":[ ["a","b"] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = [ 'a', 'b' ]
    eot           = 0
    parent        = None

    new_tree = ProvTree.ProvTree( rootname = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  argDict       = argDict, \
                                  record        = record )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ None ]      )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  # ////////////////////////////// #
  #          HELPER TOOLS          #
  # ////////////////////////////// #

  ###########################################
  #  COMPARISON PROVENANCE TREE DIMENSIONS  #
  ###########################################
  def compare_provenance_tree_dimensions( self, provTree, expected_dimensions ) :

    expected_tree_height               = expected_dimensions[ 0 ]
    expected_total_number_serial_nodes = expected_dimensions[ 1 ]

    # --------------------------------------------------------------- #
    # check tree heights

    actual_tree_height = provTree.get_tree_height()
    logging.debug( " actual_tree_height   = " + str( actual_tree_height ) )
    logging.debug( " expected_tree_height = " + str( expected_tree_height ) )
    self.assertEqual( actual_tree_height, expected_tree_height )

    # --------------------------------------------------------------- #
    # check total number of serial nodes

    actual_tree_height = provTree.get_tree_height()
    logging.debug( " actual_tree_height   = " + str( actual_tree_height ) )
    logging.debug( " expected_tree_height = " + str( expected_tree_height ) )
    self.assertEqual( actual_tree_height, expected_tree_height )


  ##########################################
  #  COMPARISON PROVENANCE GRAPH WORKFLOW  #
  ##########################################
  # specifies the steps for generating and comparing the provenance graphs of
  # input specs with expected results.
  # returns the actual provenance tree instance.
  def compare_provenance_graph_workflow( self, argDict, inputfile, serial_nodes_path, serial_edges_path, cursor, additional_str ) :

    logging.debug( "  COMPARE PROVENANCE GRAPH WORKFLOW : running process..." )

    # --------------------------------------------------------------- #
    # convert dedalus into c4 datalog and evaluate

    parsedResults = self.get_program_results( argDict, cursor )

    # --------------------------------------------------------------- #
    # build provenance tree

    # initialize provenance tree structure
    provTreeComplete = self.get_prov_tree( argDict, parsedResults, cursor, additional_str )

    # get actual serialized graph
    if serial_nodes_path :
      actual_serial_nodes = provTreeComplete.nodeset_pydot_str
    if serial_edges_path :
      actual_serial_edges = provTreeComplete.edgeset_pydot_str

    if self.PRINT_STOP :

      if serial_nodes_path :
        for n in actual_serial_nodes :
          logging.debug( "  n = " + n.rstrip() )

      if serial_nodes_path :
        for e in actual_serial_edges :
          logging.debug( "  e = " + e.rstrip() )

      tools.bp( __name__, inspect.stack()[0][3], "print stop." )

    # --------------------------------------------------------------- #
    # compare generated graphs

    if serial_nodes_path :
      expected_serial_nodes = self.get_serial( serial_nodes_path )
      self.assertEqual( actual_serial_nodes, expected_serial_nodes )

    if serial_edges_path :
      expected_serial_edges = self.get_serial( serial_edges_path )
      self.assertEqual( actual_serial_edges, expected_serial_edges )

    logging.debug( "  COMPARE PROVENANCE GRAPH WORKFLOW : ...done." )

    return provTreeComplete


  ###################
  #  GET PROV TREE  #
  ###################
  # instantiate and populate a provenance tree structure.
  # return a ProvTree object.
  def get_prov_tree( self, argDict, parsedResults, cursor, additional_str ) :

    # initialize provenance tree structure
    provTreeComplete = ProvTree.ProvTree( rootname      = "FinalState", \
                                          parsedResults = parsedResults, \
                                          cursor        = cursor, \
                                          treeType      = "goal", \
                                          isNeg         = False, \
                                          eot           = argDict[ "EOT" ], \
                                          argDict       = argDict )

    # create graph
    provTreeComplete.create_pydot_graph( 0, 0, additional_str )

    return provTreeComplete


  #########################
  #  GET PROGRAM RESULTS  #
  #########################
  # convert the input dedalus program into c4 datalog and evaluate.
  # return evaluation results dictionary.
  def get_program_results( self, argDict, cursor ) :

    # convert dedalus into c4 datalog
    allProgramData = dedt.translateDedalus( argDict, cursor )
    program_lines  = allProgramData[0]
    table_array    = allProgramData[1]

    # run c4 evaluation
    results_array = c4_evaluator.runC4_wrapper( allProgramData )
    parsedResults = tools.getEvalResults_dict_c4( results_array )

    return parsedResults


  ################
  #  GET SERIAL  #
  ################
  # grab the contents of the specified file.
  # return the list of lines as an array.
  def get_serial( self, path ) :

    serial = []

    fo = open( path, "r" )
    for line in fo :
      serial.append( line.rstrip() )
    fo.close()

    return serial


  ##################
  #  GET ARG DICT  #
  ##################
  # specify the default test arguments.
  # return dictionary.
  def getArgDict( self, inputfile ) :

    # initialize
    argDict = {}

    # populate with unit test defaults
    argDict[ 'prov_diagrams' ]            = False
    argDict[ 'use_symmetry' ]             = False
    argDict[ 'crashes' ]                  = 0
    argDict[ 'solver' ]                   = None
    argDict[ 'disable_dot_rendering' ]    = False
    argDict[ 'settings' ]                 = "./settings.ini"
    argDict[ 'negative_support' ]         = False
    argDict[ 'strategy' ]                 = None
    argDict[ 'file' ]                     = inputfile
    argDict[ 'EOT' ]                      = 4
    argDict[ 'find_all_counterexamples' ] = False
    argDict[ 'nodes' ]                    = [ "a", "b", "c" ]
    argDict[ 'evaluator' ]                = "c4"
    argDict[ 'EFF' ]                      = 2
    argDict[ 'data_save_path' ]           = "./data/"

    return argDict


if __name__ == "__main__":
  unittest.main()

#########
#  EOF  #
#########
