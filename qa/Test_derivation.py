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

from derivation import DerivTree, FactNode, GoalNode, Node, ProvTree, RuleNode, SimpNode, SimpTree, provTools

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


  #################
  #  SIMPLOG DML  #
  #################
  # tests simplog provenance graph generation without dml
  #@unittest.skip( "working on different example" )
  def test_simplog_dml( self ) :

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
    serial_nodes_path = "./testFiles/simplog_nodes_dml.txt"
    serial_edges_path = "./testFiles/simplog_edges_dml.txt"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )
    argDict[ "settings" ] = "./settings_dml.ini"

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, inputfile, serial_nodes_path, serial_edges_path, cursor )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

    tree_height               = 12
    total_number_serial_nodes = 80

    expected_dimensions = [ tree_height, \
                            total_number_serial_nodes ]

    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # sanity checks

    logging.debug( " total_number_of_descendants = " + str( provTree.get_total_number_of_descendants() ) )
    for n in provTree.get_total_descendant_list() :
      logging.debug( "    >> descendant node       = " + n )

    logging.debug( " len( serial_nodes )         = " + str( len( provTree.serial_nodes ) ) )
    for n in provTree.serial_nodes :
      logging.debug( "    >> node                  = " + n )
    logging.debug( " num_duplicate_serial_nodes  = " + str( len( provTree.get_duplicated_nodes() ) ) )
    for n in provTree.get_duplicated_nodes() :
      logging.debug( "    >> duplicated node       = " + str( n ) )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  #############
  #  SIMPLOG  #
  #############
  # tests simplog provenance graph generation without dml
  #@unittest.skip( "working on different example" )
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

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, inputfile, serial_nodes_path, serial_edges_path, cursor )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

    tree_height               = 12
    total_number_serial_nodes = 80

    expected_dimensions = [ tree_height, \
                            total_number_serial_nodes ]

    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # sanity checks

    logging.debug( " total_number_of_descendants = " + str( provTree.get_total_number_of_descendants() ) )
    for n in provTree.get_total_descendant_list() :
      logging.debug( "    >> descendant node       = " + n )

    logging.debug( " len( serial_nodes )         = " + str( len( provTree.serial_nodes ) ) )
    for n in provTree.serial_nodes :
      logging.debug( "    >> node                  = " + n )
    logging.debug( " num_duplicate_serial_nodes  = " + str( len( provTree.get_duplicated_nodes() ) ) )
    for n in provTree.get_duplicated_nodes() :
      logging.debug( "    >> duplicated node       = " + str( n ) )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 1  #
  ###############
  # tests the generation of a simple ded program execution.
  #@unittest.skip( "working on different example" )
  def test_example1( self ) :

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

    inputfile         = "./testFiles/example1.ded"
    serial_nodes_path = "./testFiles/example1_nodes.txt"
    serial_edges_path = "./testFiles/example1_edges.txt"

    # --------------------------------------------------------------- #
    # get argDict

    argDict = self.getArgDict( inputfile )

    # --------------------------------------------------------------- #
    # compare the actual provenance graph with the expected 
    # provenance graph

    provTree = self.compare_provenance_graph_workflow( argDict, inputfile, serial_nodes_path, serial_edges_path, cursor )

    # --------------------------------------------------------------- #
    # compare the actual and expected tree dimensions

    tree_height               = 14
    total_number_serial_nodes = 35

    expected_dimensions = [ tree_height, \
                            total_number_serial_nodes ]

    self.compare_provenance_tree_dimensions( provTree, expected_dimensions )

    # --------------------------------------------------------------- #
    # sanity checks

    logging.debug( " total_number_of_descendants = " + str( provTree.get_total_number_of_descendants() ) )
    for n in provTree.get_total_descendant_list() :
      logging.debug( "    >> descendant node       = " + n )

    logging.debug( " len( serial_nodes )         = " + str( len( provTree.serial_nodes ) ) )
    for n in provTree.serial_nodes :
      logging.debug( "    >> node                  = " + n )
    logging.debug( " num_duplicate_serial_nodes  = " + str( len( provTree.get_duplicated_nodes() ) ) )
    for n in provTree.get_duplicated_nodes() :
      logging.debug( "    >> duplicated node       = " + str( n ) )

    # --------------------------------------------------------------- #
    # clean up test

    IRDB.close()
    os.remove( testDB )


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
  def compare_provenance_graph_workflow( self, argDict, inputfile, serial_nodes_path, serial_edges_path, cursor ) :

    # --------------------------------------------------------------- #
    # convert dedalus into c4 datalog and evaluate

    parsedResults = self.get_program_results( argDict, cursor )

    # --------------------------------------------------------------- #
    # build provenance tree

    # initialize provenance tree structure
    provTreeComplete = self.get_prov_tree( argDict, parsedResults, cursor )

    # get actual serialized graph
    if serial_nodes_path :
      actual_serial_nodes = provTreeComplete.serial_nodes
    if serial_edges_path :
      actual_serial_edges = provTreeComplete.serial_edges

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

    return provTreeComplete


  ###################
  #  GET PROV TREE  #
  ###################
  # instantiate and populate a provenance tree structure.
  # return a ProvTree object.
  def get_prov_tree( self, argDict, parsedResults, cursor ) :

    # initialize provenance tree structure
    provTreeComplete = ProvTree.ProvTree( "FinalState", parsedResults, cursor )

    # get all post eot records
    post_eot = self.get_post_eot( parsedResults[ "post" ], argDict[ "EOT" ] )

    logging.debug( "post_eot = " + str( post_eot ) )

    # populate provenance tree
    provTreeComplete.populateTree( post_eot )

    # create graph
    provTreeComplete.createGraph( None, 0, 0, argDict )

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
  #  GET POST EOT  #
  ##################
  # extract the post results for eot only.
  # return as a list.
  def get_post_eot( self, post_results, eot ) :

    logging.debug( "  GET POST EOT : running process..." )
    logging.debug( "  GET POST EOT : eot = " + str( eot ) )

    post_eot = []

    for rec in post_results :
   
        logging.debug( "rec     = " + str( rec ) )
   
        # collect eot post records only
        if int( rec[-1] ) == int( eot ) :
          post_eot.append( rec )

    return post_eot


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
