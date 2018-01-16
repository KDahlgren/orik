#!/usr/bin/env python

'''
Test_derivation.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, sqlite3, sys, unittest

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


#####################
#  TEST DERIVATION  #
#####################
class Test_derivation( unittest.TestCase ) :

  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  PRINT_STOP = False

  # //////////////////////////////////// #
  #          FULL EXAMPLE TESTS          #
  # //////////////////////////////////// #

  ################
  #  SIMPLOG DM  #
  ################
  # tests simplog provenance graph generation without dm
  @unittest.skip( "stackoverflow." )
  def test_simplog_dm( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables(cursor)
    dedt.globalCounterReset()

    if os.path.exists( "./data/" ) :
      os.system( "rm -rf ./data/" )
    os.system( "mkdir ./data/" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile         = "./testFiles/simplog.ded"
    serial_nodes_path = "./testFiles/simplog_nodes_dm.txt"
    serial_edges_path = "./testFiles/simplog_edges_dm.txt"
    additional_str    = "_test_simplog_dm"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )
    argDict[ "settings" ] = "./settings_dm.ini"

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, \
                                                       inputfile, \
                                                       serial_nodes_path, \
                                                       serial_edges_path, \
                                                       cursor, \
                                                       additional_str )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

#    tree_height               = 12
#    total_number_serial_nodes = 80
#
#    expected_dimensions = [ tree_height, \
#                            total_number_serial_nodes ]
#
#    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #############
  #  SIMPLOG  #
  #############
  # tests simplog provenance graph generation without dm
  @unittest.skip( "stackoverflow." )
  def test_simplog( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables(cursor)
    dedt.globalCounterReset()

    if os.path.exists( "./data/" ) :
      os.system( "rm -rf ./data/" )
    os.system( "mkdir ./data/" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile         = "./testFiles/simplog.ded"
    serial_nodes_path = "./testFiles/simplog_nodes.txt"
    serial_edges_path = "./testFiles/simplog_edges.txt"
    additional_str    = "_test_simplog"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, \
                                                       inputfile, \
                                                       serial_nodes_path, \
                                                       serial_edges_path, \
                                                       cursor, \
                                                       additional_str )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

#    tree_height               = 12
#    total_number_serial_nodes = 80
#
#    expected_dimensions = [ tree_height, \
#                            total_number_serial_nodes ]
#
#    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 2  #
  ##############
  # tests a small dedalus program
  # such that one relation is both idb and edb.
  #@unittest.skip( "working on different example" )
  def test_example_2( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables(cursor)
    dedt.globalCounterReset()

    if os.path.exists( "./data/" ) :
      os.system( "rm -rf ./data/" )
    os.system( "mkdir ./data/" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile         = "./testFiles/example_2.ded"
    serial_nodes_path = "./testFiles/example_2_expected_nodes.txt"
    serial_edges_path = "./testFiles/example_2_expected_edges.txt"
    additional_str    = "_test_example_2"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )
    argDict[ "EOT" ] = 1

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    # instantiate tree
    try :
      provTree = self.compare_provenance_graph_workflow( argDict, \
                                                         inputfile, \
                                                         serial_nodes_path, \
                                                         serial_edges_path, \
                                                         cursor, \
                                                         additional_str )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.RuleNode at function generate_descendant_meta :\n>>>   FATAL ERROR : subgoal 't' is both edb and idb. ambiguous. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

#    tree_height               = 12
#    total_number_serial_nodes = 80
#
#    expected_dimensions = [ tree_height, \
#                            total_number_serial_nodes ]
#
#    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  ###############
  #  EXAMPLE 1  #
  ##############
  # tests a small dedalus program
  #@unittest.skip( "working on different example" )
  def test_example_1( self ) :

    # --------------------------------------------------------------- #
    # set up test

    if os.path.exists( "./IR.db" ) :
      os.remove( "./IR.db" )

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables(cursor)
    dedt.globalCounterReset()

    if os.path.exists( "./data/" ) :
      os.system( "rm -rf ./data/" )
    os.system( "mkdir ./data/" )

    # --------------------------------------------------------------- #
    # specify input file paths

    inputfile         = "./testFiles/example_1.ded"
    serial_nodes_path = "./testFiles/example_1_expected_nodes.txt"
    serial_edges_path = "./testFiles/example_1_expected_edges.txt"
    additional_str    = "_test_example_1"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )
    argDict[ "EOT" ] = 1

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, \
                                                       inputfile, \
                                                       serial_nodes_path, \
                                                       serial_edges_path, \
                                                       cursor, \
                                                       additional_str )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

#    tree_height               = 12
#    total_number_serial_nodes = 80
#
#    expected_dimensions = [ tree_height, \
#                            total_number_serial_nodes ]
#
#    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  # ///////////////////////////////////// #
  #          FUNCTIONALITY TESTS          #
  # ///////////////////////////////////// #


  #################
  #  PROV TREE 8  #
  #################
  # test generating a provenance graph in which 
  # a rule is defined recursively.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_8( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','t','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','1','T','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','t','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','1','T','int')" )

    # t rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('2','t','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','m','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','T','int')" )

    # t provenance rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('3','t_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','m','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','1','0','T','int')" )

    # t rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('4','t','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','1','T+1','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','0','t','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','1','0','T','int')" )

    # t provenance rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('5','t_prov2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','1','T+1','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','0','t','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','1','0','T','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('7','t','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('7','0','\"a\"','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('7','1','1','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('8','t','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','0','\"b\"','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','1','1','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('9','c','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('9','0','1','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','2'], ['b','2'] ], \
                      "post_prov0":[ ['a','2'], ['b','2'] ], \
                      "t":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "t_prov1":[ ['a','1'], ['b','1'] ], \
                      "t_prov2":[ ['a','2'], ['b','2'] ], \
                      "m":[ ['a','1'] ], \
                      "c":[ ['1'] ] }

    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 2
    parent        = None

    # instantiate tree
    try :
      new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                    parsedResults = parsedResults, \
                                    cursor        = cursor, \
                                    treeType      = treeType, \
                                    isNeg         = isNeg, \
                                    eot           = eot )

    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.RuleNode at function generate_descendant_meta :\n>>>   FATAL ERROR : subgoal 't' is both edb and idb. ambiguous. aborting."

    self.assertEqual( actual_error, expected_error )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    if os.path.exists( testDB ) :
      os.remove( testDB )


  #################
  #  PROV TREE 7  #
  #################
  # test generating a provenance graph in which 
  # a rule contains an agg in the goal.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_7( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','t','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','1','T','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','t','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','1','T','int')" )

    # t rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('2','t','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','m','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','T','int')" )

    # t provenance rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('3','t_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','1','T','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','m','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','1','0','T','int')" )

    # t rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('4','t','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','1','T+1','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','0','t','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','1','0','T','int')" )

    # t provenance rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('5','t_prov2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','1','T+1','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','0','t','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','1','c','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','T','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','1','0','T','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('7','m','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('7','0','\"a\"','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('7','1','1','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('8','m','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','0','\"b\"','string')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','1','1','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('9','c','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('9','0','1','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','2'], ['b','2'] ], \
                      "post_prov0":[ ['a','2'], ['b','2'] ], \
                      "t":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "t_prov1":[ ['a','1'], ['b','1'] ], \
                      "t_prov2":[ ['a','2'], ['b','2'] ], \
                      "m":[ ['a','1'] ], \
                      "c":[ ['1'] ] }

    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 2
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    logging.debug( " node_str_to_object_map :" )
    logging.debug( new_tree.node_str_to_object_map )
    logging.debug( len( new_tree.node_str_to_object_map ) )
    logging.debug( " nodeset_pydot :" )
    logging.debug( new_tree.nodeset_pydot )
    logging.debug( len( new_tree.nodeset_pydot ) )
    logging.debug( " nodeset_pydot_str :" )
    logging.debug( new_tree.nodeset_pydot_str )
    logging.debug( len( new_tree.nodeset_pydot_str ) )
    logging.debug( " edgeset_pydot :" )
    logging.debug( new_tree.edgeset_pydot )
    logging.debug( len( new_tree.edgeset_pydot ) )
    logging.debug( " edgeset_pydot_str :" )
    logging.debug( new_tree.edgeset_pydot_str )
    logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_7" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 16 )
    self.assertTrue( graph_stats[ "num_edges" ] == 18 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #################
  #  PROV TREE 6  #
  #################
  # test generating a provenance containing an idb with multiple rule definitions.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_6( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','int')" )

    # sub1 rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','int')" )

    # sub1 provenance rule 1
    cursor.execute( "INSERT INTO Rule       VALUES ('3','sub1_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','int')" )

    # sub1 rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('4','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','X','int')" )

    # sub1 provenance rule 2
    cursor.execute( "INSERT INTO Rule       VALUES ('5','sub1_prov2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','X','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('6','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('6','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('7','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('7','0','b','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('8','sub2','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','0','1','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('9','sub3','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('9','0','1','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','1'], ['b','1'] ], \
                      "post_prov0":[ ['a','1'], ['b','1'] ], \
                      "sub0":[ ['a'], ['b'] ], \
                      "sub1":[ ['1'] ], \
                      "sub1_prov1":[ ['1'] ], \
                      "sub1_prov2":[ ['1'] ], \
                      "sub2":[ ['1'] ], \
                      "sub3":[ ['2'] ] }

    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 1
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '1'])" ]
    goal_post_a_1_parents  = goal_post_a_1_rootname.parents
    self.assertTrue( len( goal_post_a_1_parents ) == 1 )

    goal_post_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '1'])" ]
    goal_post_b_1_parents  = goal_post_b_1_rootname.parents
    self.assertTrue( len( goal_post_b_1_parents ) == 1 )

    rule_post_prov0_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '1'])" ]
    rule_post_prov0_a_1_parents  = rule_post_prov0_a_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_1_parents ) == 1 )

    rule_post_prov0_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '1'])" ]
    rule_post_prov0_b_1_parents  = rule_post_prov0_b_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_1_parents ) == 1 )

    fact_sub0_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['a'])" ]
    fact_sub0_a_parents  = fact_sub0_a_rootname.parents
    self.assertTrue( len( fact_sub0_a_parents ) == 1 )

    goal_sub2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub1(['1'])" ]
    goal_sub2_1_parents  = goal_sub2_1_rootname.parents
    self.assertTrue( len( goal_sub2_1_parents ) == 2 )

    fact_sub0_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['b'])" ]
    fact_sub0_b_parents  = fact_sub0_b_rootname.parents
    self.assertTrue( len( fact_sub0_b_parents ) == 1 )

    rule_sub1_prov1_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov1(['1'])" ]
    rule_sub1_prov1_1_parents  = rule_sub1_prov1_1_rootname.parents
    self.assertTrue( len( rule_sub1_prov1_1_parents ) == 1 )

    rule_sub1_prov2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov2(['1'])" ]
    rule_sub1_prov2_1_parents  = rule_sub1_prov2_1_rootname.parents
    self.assertTrue( len( rule_sub1_prov2_1_parents ) == 1 )

    fact_sub2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub2(['1'])" ]
    fact_sub2_1_parents  = fact_sub2_1_rootname.parents
    self.assertTrue( len( fact_sub2_1_parents ) == 1 )

    fact_sub3_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub3(['1'])" ]
    fact_sub3_1_parents  = fact_sub3_1_rootname.parents
    self.assertTrue( len( fact_sub3_1_parents ) == 1 )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    logging.debug( " node_str_to_object_map :" )
    logging.debug( new_tree.node_str_to_object_map )
    logging.debug( len( new_tree.node_str_to_object_map ) )
    logging.debug( " nodeset_pydot :" )
    logging.debug( new_tree.nodeset_pydot )
    logging.debug( len( new_tree.nodeset_pydot ) )
    logging.debug( " nodeset_pydot_str :" )
    logging.debug( new_tree.nodeset_pydot_str )
    logging.debug( len( new_tree.nodeset_pydot_str ) )
    logging.debug( " edgeset_pydot :" )
    logging.debug( new_tree.edgeset_pydot )
    logging.debug( len( new_tree.edgeset_pydot ) )
    logging.debug( " edgeset_pydot_str :" )
    logging.debug( new_tree.edgeset_pydot_str )
    logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_6" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 12 )
    self.assertTrue( graph_stats[ "num_edges" ] == 12 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )



  #################
  #  PROV TREE 5  #
  #################
  # test generating a provenance containing a negated idb.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_5( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','2','sub2','notin','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','2','0','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','2','sub2','notin','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','2','0','Y','int')" )

    # sub2 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','sub2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','int')" )

    # sub2 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','sub2_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('2','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('2','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','b','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('4','sub1','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','0','1','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('5','sub3','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('5','0','2','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','1'], ['b','1'] ], \
                      "post_prov0":[ ['a','1'], ['b','1'] ], \
                      "sub0":[ ['a'], ['b'] ], \
                      "sub1":[ ['1'] ], \
                      "sub2":[ ['2'] ], \
                      "sub2_prov1":[ ['2'] ], \
                      "sub3":[ ['2'] ] }

    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 1
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '1'])" ]
    goal_post_a_1_parents  = goal_post_a_1_rootname.parents
    self.assertTrue( len( goal_post_a_1_parents ) == 1 )

    goal_post_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '1'])" ]
    goal_post_b_1_parents  = goal_post_b_1_rootname.parents
    self.assertTrue( len( goal_post_b_1_parents ) == 1 )

    rule_post_prov0_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '1'])" ]
    rule_post_prov0_a_1_parents  = rule_post_prov0_a_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_1_parents ) == 1 )

    rule_post_prov0_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '1'])" ]
    rule_post_prov0_b_1_parents  = rule_post_prov0_b_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_1_parents ) == 1 )

    fact_sub0_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['a'])" ]
    fact_sub0_a_parents  = fact_sub0_a_rootname.parents
    self.assertTrue( len( fact_sub0_a_parents ) == 1 )

    fact_sub1_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub1(['1'])" ]
    fact_sub1_1_parents  = fact_sub1_1_rootname.parents
    self.assertTrue( len( fact_sub1_1_parents ) == 2 )

    goal_not_sub2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->_NOT_sub2(['1'])" ]
    goal_not_sub2_1_parents  = goal_not_sub2_1_rootname.parents
    self.assertTrue( len( goal_not_sub2_1_parents ) == 2 )

    fact_sub0_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['b'])" ]
    fact_sub0_b_parents  = fact_sub0_b_rootname.parents
    self.assertTrue( len( fact_sub0_b_parents ) == 1 )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    logging.debug( " node_str_to_object_map :" )
    logging.debug( new_tree.node_str_to_object_map )
    logging.debug( len( new_tree.node_str_to_object_map ) )
    logging.debug( " nodeset_pydot :" )
    logging.debug( new_tree.nodeset_pydot )
    logging.debug( len( new_tree.nodeset_pydot ) )
    logging.debug( " nodeset_pydot_str :" )
    logging.debug( new_tree.nodeset_pydot_str )
    logging.debug( len( new_tree.nodeset_pydot_str ) )
    logging.debug( " edgeset_pydot :" )
    logging.debug( new_tree.edgeset_pydot )
    logging.debug( len( new_tree.edgeset_pydot ) )
    logging.debug( " edgeset_pydot_str :" )
    logging.debug( new_tree.edgeset_pydot_str )
    logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_5" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 9 )
    self.assertTrue( graph_stats[ "num_edges" ] == 10 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #################
  #  PROV TREE 4  #
  #################
  # test generating a provenance containing a negated fact.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_4( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','2','sub2','notin','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','2','0','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','2','sub2','notin','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','2','0','Y','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('2','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('2','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('3','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('3','0','b','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('4','sub1','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','0','1','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('5','sub2','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('5','0','2','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','1'], ['b','1'] ], \
                      "post_prov0":[ ['a','1'], ['b','1'] ], \
                      "sub0":[ ['a'], ['b'] ], \
                      "sub1":[ ['1'] ], \
                      "sub2":[ ['2'] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 1
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '1'])" ]
    goal_post_a_1_parents  = goal_post_a_1_rootname.parents
    self.assertTrue( len( goal_post_a_1_parents ) == 1 )

    goal_post_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '1'])" ]
    goal_post_b_1_parents  = goal_post_b_1_rootname.parents
    self.assertTrue( len( goal_post_b_1_parents ) == 1 )

    rule_post_prov0_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '1'])" ]
    rule_post_prov0_a_1_parents  = rule_post_prov0_a_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_1_parents ) == 1 )

    rule_post_prov0_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '1'])" ]
    rule_post_prov0_b_1_parents  = rule_post_prov0_b_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_1_parents ) == 1 )

    fact_sub0_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['a'])" ]
    fact_sub0_a_parents  = fact_sub0_a_rootname.parents
    self.assertTrue( len( fact_sub0_a_parents ) == 1 )

    fact_sub1_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub1(['1'])" ]
    fact_sub1_1_parents  = fact_sub1_1_rootname.parents
    self.assertTrue( len( fact_sub1_1_parents ) == 2 )

    fact_not_sub2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->_NOT_sub2(['1'])" ]
    fact_not_sub2_1_parents  = fact_not_sub2_1_rootname.parents
    self.assertTrue( len( fact_not_sub2_1_parents ) == 2 )

    fact_sub0_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['b'])" ]
    fact_sub0_b_parents  = fact_sub0_b_rootname.parents
    self.assertTrue( len( fact_sub0_b_parents ) == 1 )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    #logging.debug( " node_str_to_object_map :" )
    #logging.debug( new_tree.node_str_to_object_map )
    #logging.debug( len( new_tree.node_str_to_object_map ) )
    #logging.debug( " nodeset_pydot :" )
    #logging.debug( new_tree.nodeset_pydot )
    #logging.debug( len( new_tree.nodeset_pydot ) )
    #logging.debug( " nodeset_pydot_str :" )
    #logging.debug( new_tree.nodeset_pydot_str )
    #logging.debug( len( new_tree.nodeset_pydot_str ) )
    #logging.debug( " edgeset_pydot :" )
    #logging.debug( new_tree.edgeset_pydot )
    #logging.debug( len( new_tree.edgeset_pydot ) )
    #logging.debug( " edgeset_pydot_str :" )
    #logging.debug( new_tree.edgeset_pydot_str )
    #logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_4" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 9 )
    self.assertTrue( graph_stats[ "num_edges" ] == 10 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #################
  #  PROV TREE 3  #
  #################
  # test generating a provenance containing a goal node with two parents.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_3( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','1','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','1','Y','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','int')" )

    # sub0 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','int')" )

    # sub0 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('3','sub0_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','1','0','Y','int')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('4','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','0','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','X','int')" )

    # sub1 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('5','sub1_prov2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','0','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','X','int')" )

    # sub4 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('6','sub4','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('6','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('6','0','sub5','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('6','0','0','X','int')" )

    # sub4 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('7','sub4_prov3','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('7','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('7','0','sub5','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('7','0','0','X','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('8','sub3','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('9','sub3','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('9','0','b','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('10','sub5','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('10','0','1','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('11','sub5','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('11','0','2','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','2'], ['b','2'] ], \
                      "post_prov0":[ ['a','2'], ['b','2'] ], \
                      "sub0":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub0_prov1":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub1":[ ['1'], ['2'] ], \
                      "sub1_prov2":[ ['1'], ['2'] ], \
                      "sub4":[ ['1'], ['2'] ], \
                      "sub4_prov3":[ ['1'], ['2'] ], \
                      "sub3":[ ['a'], ['b'] ], \
                      "sub5":[ ['1'], ['2'] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 2
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '2'])" ]
    goal_post_a_2_parents  = goal_post_a_2_rootname.parents
    self.assertTrue( len( goal_post_a_2_parents ) == 1 )

    goal_post_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '2'])" ]
    goal_post_b_2_parents  = goal_post_b_2_rootname.parents
    self.assertTrue( len( goal_post_b_2_parents ) == 1 )

    rule_post_prov0_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '2'])" ]
    rule_post_prov0_a_2_parents  = rule_post_prov0_a_2_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_2_parents ) == 1 )

    rule_post_prov0_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '2'])" ]
    rule_post_prov0_b_2_parents  = rule_post_prov0_b_2_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_2_parents ) == 1 )

    goal_sub0_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub0(['a', '2'])" ]
    goal_sub0_a_2_parents  = goal_sub0_a_2_rootname.parents
    self.assertTrue( len( goal_sub0_a_2_parents ) == 1 )

    goal_sub1_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub1(['2'])" ]
    goal_sub1_2_parents  = goal_sub1_2_rootname.parents
    self.assertTrue( len( goal_sub1_2_parents ) == 2 )

    goal_sub0_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub0(['b', '2'])" ]
    goal_sub0_b_2_parents  = goal_sub0_b_2_rootname.parents
    self.assertTrue( len( goal_sub0_b_2_parents ) == 1 )

    rule_sub0_prov1_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['a', '2'])" ]
    rule_sub0_prov1_a_2_parents  = rule_sub0_prov1_a_2_rootname.parents
    self.assertTrue( len( rule_sub0_prov1_a_2_parents ) == 1 )

    rule_sub1_prov2_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov2(['2'])" ]
    rule_sub1_prov2_2_parents  = rule_sub1_prov2_2_rootname.parents
    self.assertTrue( len( rule_sub1_prov2_2_parents ) == 1 )

    rule_sub0_prov1_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['b', '2'])" ]
    rule_sub0_prov1_b_2_parents  = rule_sub0_prov1_b_2_rootname.parents
    self.assertTrue( len( rule_sub0_prov1_b_2_parents ) == 1 )

    fact_sub3_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub3(['a'])" ]
    fact_sub3_a_parents  = fact_sub3_a_rootname.parents
    self.assertTrue( len( fact_sub3_a_parents ) == 1 )

    goal_sub4_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub4(['2'])" ]
    goal_sub4_2_parents  = goal_sub4_2_rootname.parents
    self.assertTrue( len( goal_sub4_2_parents ) == 3 )

    fact_sub3_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub3(['b'])" ]
    fact_sub3_b_parents  = fact_sub3_b_rootname.parents
    self.assertTrue( len( fact_sub3_b_parents ) == 1 )

    rule_sub4_prov3_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub4_prov3(['2'])" ]
    rule_sub4_prov3_2_parents  = rule_sub4_prov3_2_rootname.parents
    self.assertTrue( len( rule_sub4_prov3_2_parents ) == 1 )

    fact_sub5_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub5(['2'])" ]
    fact_sub5_2_parents  = fact_sub5_2_rootname.parents
    self.assertTrue( len( fact_sub5_2_parents ) == 1 )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    #logging.debug( " node_str_to_object_map :" )
    #logging.debug( new_tree.node_str_to_object_map )
    #logging.debug( len( new_tree.node_str_to_object_map ) )
    #logging.debug( " nodeset_pydot :" )
    #logging.debug( new_tree.nodeset_pydot )
    #logging.debug( len( new_tree.nodeset_pydot ) )
    #logging.debug( " nodeset_pydot_str :" )
    #logging.debug( new_tree.nodeset_pydot_str )
    #logging.debug( len( new_tree.nodeset_pydot_str ) )
    #logging.debug( " edgeset_pydot :" )
    #logging.debug( new_tree.edgeset_pydot )
    #logging.debug( len( new_tree.edgeset_pydot ) )
    #logging.debug( " edgeset_pydot_str :" )
    #logging.debug( new_tree.edgeset_pydot_str )
    #logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_3" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 16 )
    self.assertTrue( graph_stats[ "num_edges" ] == 18 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #################
  #  PROV TREE 2  #
  #################
  # test generating a provenance containing a goal with 
  # two parents and a fact with two parents.
  # also tests wilcards.
  #@unittest.skip( "working on different exampple." )
  def test_prov_tree_2( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','1','_','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','_','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','1','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','1','_','int')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','_','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','1','Y','int')" )

    # sub0 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','1','0','Y','int')" )

    # sub0 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('3','sub0_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','1','0','Y','int')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('4','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('4','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('4','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('4','1','0','Y','int')" )

    # sub1 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('5','sub1_prov2','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('5','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','0','sub3','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','0','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('5','1','sub4','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('5','1','0','Y','int')" )

    # sub3 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('6','sub3','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('6','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('6','0','sub5','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('6','0','0','X','string')" )

    # sub3 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('7','sub3_prov3','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('7','0','X','string')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('7','0','sub5','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('7','0','0','X','string')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('8','sub4','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('8','0','1','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('9','sub4','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('9','0','2','int')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('10','sub5','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('10','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('11','sub5','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('11','0','b','string')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','2'], ['b','2'] ], \
                      "post_prov0":[ ['a','2'], ['b','2'] ], \
                      "sub0":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub1":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub0_prov1":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub1_prov2":[ ['a','1'], ['b','1'], ['a','2'], ['b','2'] ], \
                      "sub3":[ ['a'], ['b'] ], \
                      "sub3_prov3":[ ['a'], ['b'] ], \
                      "sub4":[ ['1'], ['2'] ], \
                      "sub5":[ ['a'], ['b'] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 2
    parent        = None

    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '2'])" ]
    goal_post_a_2_parents  = goal_post_a_2_rootname.parents
    self.assertTrue( len( goal_post_a_2_parents ) == 1 )

    goal_post_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '2'])" ]
    goal_post_b_2_parents  = goal_post_b_2_rootname.parents
    self.assertTrue( len( goal_post_b_2_parents ) == 1 )

    rule_post_prov0_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '2'])" ]
    rule_post_prov0_a_2_parents  = rule_post_prov0_a_2_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_2_parents ) == 1 )

    rule_post_prov0_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '2'])" ]
    rule_post_prov0_b_2_parents  = rule_post_prov0_b_2_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_2_parents ) == 1 )

    goal_sub0_a___rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub0(['a', '_'])" ]
    goal_sub0_a___parents  = goal_sub0_a___rootname.parents
    self.assertTrue( len( goal_sub0_a___parents ) == 1 )

    goal_sub1___2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub1(['_', '2'])" ]
    goal_sub1___2_parents  = goal_sub1___2_rootname.parents
    self.assertTrue( len( goal_sub1___2_parents ) == 2 )

    goal_sub1_b___rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub0(['b', '_'])" ]
    goal_sub1_b___parents  = goal_sub1_b___rootname.parents
    self.assertTrue( len( goal_sub1_b___parents ) == 1 )

    rule_sub0_prov1_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['a', '1'])" ]
    rule_sub0_prov1_a_1_parents  = rule_sub0_prov1_a_1_rootname.parents
    self.assertTrue( len( rule_sub0_prov1_a_1_parents ) == 1 )

    rule_sub0_prov1_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['a', '2'])" ]
    rule_sub0_prov1_a_2_parents  = rule_sub0_prov1_a_2_rootname.parents
    logging.debug( "  rule_sub0_prov1_a_2_parents = " + str(rule_sub0_prov1_a_2_parents) )
    self.assertTrue( len( rule_sub0_prov1_a_2_parents ) == 1 )

    rule_sub1_prov2_a_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov2(['a', '2'])" ]
    rule_sub1_prov2_a_2_parents  = rule_sub1_prov2_a_2_rootname.parents
    self.assertTrue( len( rule_sub1_prov2_a_2_parents ) == 1 )

    rule_sub1_prov2_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov2(['b', '2'])" ]
    rule_sub1_prov2_b_2_parents  = rule_sub1_prov2_b_2_rootname.parents
    self.assertTrue( len( rule_sub1_prov2_b_2_parents ) == 1 )

    rule_sub0_prov1_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['b', '1'])" ]
    rule_sub0_prov1_b_1_parents  = rule_sub0_prov1_a_2_rootname.parents
    self.assertTrue( len( rule_sub0_prov1_b_1_parents ) == 1 )

    rule_sub0_prov1_b_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub0_prov1(['b', '2'])" ]
    rule_sub0_prov1_b_2_parents  = rule_sub0_prov1_b_2_rootname.parents
    self.assertTrue( len( rule_sub0_prov1_b_2_parents ) == 1 )

    goal_sub3_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub3(['a'])" ]
    goal_sub3_a_parents  = goal_sub3_a_rootname.parents
    self.assertTrue( len( goal_sub3_a_parents ) == 3 )

    fact_sub4_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub4(['1'])" ]
    fact_sub4_1_parents  = fact_sub4_1_rootname.parents
    self.assertTrue( len( fact_sub4_1_parents ) == 2 )

    fact_sub4_2_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub4(['2'])" ]
    fact_sub4_2_parents  = fact_sub4_2_rootname.parents
    self.assertTrue( len( fact_sub4_2_parents ) == 4 )

    goal_sub3_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub3(['b'])" ]
    goal_sub3_b_parents  = goal_sub3_b_rootname.parents
    self.assertTrue( len( goal_sub3_b_parents ) == 3 )

    rule_sub3_prov3_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub3_prov3(['a'])" ]
    rule_sub3_prov3_a_parents  = rule_sub3_prov3_a_rootname.parents
    self.assertTrue( len( rule_sub3_prov3_a_parents ) == 1 )

    rule_sub3_prov3_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub3_prov3(['b'])" ]
    rule_sub3_prov3_b_parents  = rule_sub3_prov3_b_rootname.parents
    self.assertTrue( len( rule_sub3_prov3_b_parents ) == 1 )

    fact_sub5_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub5(['a'])" ]
    fact_sub5_a_parents  = fact_sub5_a_rootname.parents
    self.assertTrue( len( fact_sub5_a_parents ) == 1 )

    fact_sub5_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub5(['b'])" ]
    fact_sub5_b_parents  = fact_sub5_b_rootname.parents
    self.assertTrue( len( fact_sub5_b_parents ) == 1 )

    # ------------------------------------------- #
    # generate graph visualisation and 
    # examine stats

    #logging.debug( " node_str_to_object_map :" )
    #logging.debug( new_tree.node_str_to_object_map )
    #logging.debug( len( new_tree.node_str_to_object_map ) )
    #logging.debug( " nodeset_pydot :" )
    #logging.debug( new_tree.nodeset_pydot )
    #logging.debug( len( new_tree.nodeset_pydot ) )
    #logging.debug( " nodeset_pydot_str :" )
    #logging.debug( new_tree.nodeset_pydot_str )
    #logging.debug( len( new_tree.nodeset_pydot_str ) )
    #logging.debug( " edgeset_pydot :" )
    #logging.debug( new_tree.edgeset_pydot )
    #logging.debug( len( new_tree.edgeset_pydot ) )
    #logging.debug( " edgeset_pydot_str :" )
    #logging.debug( new_tree.edgeset_pydot_str )
    #logging.debug( len( new_tree.edgeset_pydot_str ) )

    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_2" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 22 )
    self.assertTrue( graph_stats[ "num_edges" ] == 30 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #################
  #  PROV TREE 1  #
  #################
  # test generating a provenance containing a goal with two parents.
  #@unittest.skip( "working on different example." )
  def test_prov_tree_1( self ) :

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

    # post rule
    cursor.execute( "INSERT INTO Rule       VALUES ('0','post','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('0','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('0','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('0','1','0','Y','int')" )

    # post provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('1','post_prov0','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','0','X','string')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('1','1','Y','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','0','sub0','','')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('1','1','sub1','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','0','0','X','string')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('1','1','0','Y','int')" )

    # sub1 rule
    cursor.execute( "INSERT INTO Rule       VALUES ('2','sub1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('2','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('2','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('2','0','0','X','int')" )

    # sub1 provenance rule
    cursor.execute( "INSERT INTO Rule       VALUES ('3','sub1_prov1','','')" )
    cursor.execute( "INSERT INTO GoalAtt    VALUES ('3','0','X','int')" )
    cursor.execute( "INSERT INTO Subgoals   VALUES ('3','0','sub2','','')" )
    cursor.execute( "INSERT INTO SubgoalAtt VALUES ('3','0','0','X','int')" )

    # fact data
    cursor.execute( "INSERT INTO Fact     VALUES ('4','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('4','0','a','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('5','sub0','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('5','0','b','string')" )
    cursor.execute( "INSERT INTO Fact     VALUES ('6','sub2','')" )
    cursor.execute( "INSERT INTO FactData VALUES ('6','0','1','int')" )

    # ------------------------------------------- #
    # instantiate new tree

    rootname      = "FinalState"
    parsedResults = { "post":[ ['a','1'], ['b','1'] ], \
                      "sub0":[ ['a'], ['b'] ], \
                      "sub1":[ ['1'] ], \
                      "sub1_prov1":[ ['1'] ], \
                      "sub2":[ ['1'] ], \
                      "post_prov0":[ ['a','1'], ['b','1'] ] }
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 1
    parent        = None

    # instantiate tree
    new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                  parsedResults = parsedResults, \
                                  cursor        = cursor, \
                                  treeType      = treeType, \
                                  isNeg         = isNeg, \
                                  eot           = eot )

    self.assertTrue( new_tree.rootname      == rootname      )
    self.assertTrue( new_tree.parsedResults == parsedResults )
    self.assertTrue( new_tree.cursor        == cursor        )
    self.assertTrue( new_tree.db_id         == db_id         )
    self.assertTrue( new_tree.treeType      == treeType      )
    self.assertTrue( new_tree.isNeg         == isNeg         )
    self.assertTrue( new_tree.provAttMap    == provAttMap    )
    self.assertTrue( new_tree.record        == record        )
    self.assertTrue( new_tree.eot           == eot           )
    self.assertTrue( new_tree.parents       == [ ]           )

    # ------------------------------------------- #
    # examine descendants

    # get post descendant list
    actual_list_of_descendants_curr_nodes   = [ d.curr_node for d in new_tree.descendants ]

    self.assertTrue( type( actual_list_of_descendants_curr_nodes[ 0 ] ) is GoalNode.GoalNode   )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 0 ].name          == "post"        )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 0 ].isNeg         == False         )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 0 ].record        == [ 'a', '1' ]    )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 0 ].parsedResults == parsedResults )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 0 ].cursor        == cursor        )

    self.assertTrue( type( actual_list_of_descendants_curr_nodes[ 1 ] ) is GoalNode.GoalNode   )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 1 ].name          == "post"        )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 1 ].isNeg         == False         )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 1 ].record        == [ 'b', '1' ]    )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 1 ].parsedResults == parsedResults )
    self.assertTrue( actual_list_of_descendants_curr_nodes[ 1 ].cursor        == cursor        )

    final_state_parents  = new_tree.parents
    self.assertTrue( len( final_state_parents ) == 0 )

    goal_post_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['a', '1'])" ]
    goal_post_a_1_parents  = goal_post_a_1_rootname.parents
    self.assertTrue( len( goal_post_a_1_parents ) == 1 )

    goal_post_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->post(['b', '1'])" ]
    goal_post_b_1_parents  = goal_post_b_1_rootname.parents
    self.assertTrue( len( goal_post_b_1_parents ) == 1 )

    rule_post_prov0_a_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['a', '1'])" ]
    rule_post_prov0_a_1_parents  = rule_post_prov0_a_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_a_1_parents ) == 1 )

    rule_post_prov0_b_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->post_prov0(['b', '1'])" ]
    rule_post_prov0_b_1_parents  = rule_post_prov0_b_1_rootname.parents
    self.assertTrue( len( rule_post_prov0_b_1_parents ) == 1 )

    fact_sub0_a_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['a'])" ]
    fact_sub0_a_parents  = fact_sub0_a_rootname.parents
    self.assertTrue( len( fact_sub0_a_parents ) == 1 )

    goal_sub1_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "goal->sub1(['1'])" ]
    goal_sub1_1_parents  = goal_sub1_1_rootname.parents
    self.assertTrue( len( goal_sub1_1_parents ) == 2 )

    fact_sub0_b_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub0(['b'])" ]
    fact_sub0_b_parents  = fact_sub0_b_rootname.parents
    self.assertTrue( len( fact_sub0_b_parents ) == 1 )

    rule_sub1_prov1_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "rule->sub1_prov1(['1'])" ]
    rule_sub1_prov1_1_parents  = rule_sub1_prov1_1_rootname.parents
    self.assertTrue( len( rule_sub1_prov1_1_parents ) == 1 )

    fact_sub2_1_rootname = new_tree.final_state_ptr.node_str_to_object_map[ "fact->sub2(['1'])" ]
    fact_sub2_1_parents  = fact_sub2_1_rootname.parents
    self.assertTrue( len( fact_sub2_1_parents ) == 1 )

    # ------------------------------------------- #

    #logging.debug( " node_str_to_object_map :" )
    #logging.debug( new_tree.node_str_to_object_map )
    #logging.debug( len( new_tree.node_str_to_object_map ) )
    #logging.debug( " nodeset_pydot :" )
    #logging.debug( new_tree.nodeset_pydot )
    #logging.debug( len( new_tree.nodeset_pydot ) )
    #logging.debug( " nodeset_pydot_str :" )
    #logging.debug( new_tree.nodeset_pydot_str )
    #logging.debug( len( new_tree.nodeset_pydot_str ) )
    #logging.debug( " edgeset_pydot :" )
    #logging.debug( new_tree.edgeset_pydot )
    #logging.debug( len( new_tree.edgeset_pydot ) )
    #logging.debug( " edgeset_pydot_str :" )
    #logging.debug( new_tree.edgeset_pydot_str )
    #logging.debug( len( new_tree.edgeset_pydot_str ) )

    # generate graph visualisation and examine stats
    graph_stats = new_tree.create_pydot_graph( 0, 0, "_test_prov_tree_1" )
    self.assertTrue( graph_stats[ "num_nodes" ] == 10 )
    self.assertTrue( graph_stats[ "num_edges" ] == 10 )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )
  

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

    new_rule_node = RuleNode.RuleNode( rid           = rid, \
                                       name          = name, \
                                       record        = record, \
                                       parsedResults = parsedResults, \
                                       cursor        = cursor )

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
    expected_error = "BREAKPOINT in file derivation.GoalNode at function get_prov_rid_and_name_list :\n>>>   FATAL ERROR : no provenance rule for 'TestNode'"

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

    rootname      = "__KD__TESTNODE__KD__1"
    parsedResults = { "__KD__TESTNODE__KD__1":[ ['a','b'] ] }
    cursor        = None
    db_id         = None
    treeType      = "goal"
    isNeg         = False
    provAttMap    = {}
    record        = []
    eot           = 0
    parent        = None

    try :
      new_tree = ProvTree.ProvTree( rootname      = rootname, \
                                    parsedResults = parsedResults, \
                                    treeType      = treeType, \
                                    isNeg         = isNeg )
    except SystemExit :
      actual_error = str( sys.exc_info()[1] )

    # define expected error
    expected_error = "BREAKPOINT in file derivation.GoalNode at function __init__ :\n>>>   GOAL CONSTRUCTOR : FATAL ERROR : record '[]' does not appear in the results for relation '__KD__TESTNODE__KD__1' :\n[['a', 'b']]"

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

    testDB = "./IR.db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables( cursor )
    dedt.globalCounterReset()

    # --------------------------------------------------------------- #

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

    return argDict


#########
#  EOF  #
#########
