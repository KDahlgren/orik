#!/usr/bin/env python
  
'''
Test_combo_sip.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, re, string, sqlite3, sys, unittest

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


####################
#  TEST COMBO SIP  #
####################
class Test_combo_sip( unittest.TestCase ) :

  logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.DEBUG )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.INFO )
  #logging.basicConfig( format='%(levelname)s:%(message)s', level=logging.WARNING )

  PRINT_STOP = False

  #############
  #  SIMPLOG  #
  #############
  #@unittest.skip( "works." )
  def test_simplog( self ) :

    test_id        = "simplog"
    test_file_name = "simplog_driver"

    print " >>> RUNNING " + test_id + " <<<"

    test_id           = "combo_sip_" + test_id
    serial_nodes_path = "./testFiles/" + test_id + "_expected_nodes.txt"
    serial_edges_path = "./testFiles/" + test_id + "_expected_edges.txt"

    input_file                  = "./dedalus_drivers/" + test_file_name + ".ded"
    argDict                     = self.getArgDict( input_file )
    argDict[ 'data_save_path' ] = "./data/" + test_id + "/"
    argDict[ 'EOT' ]            = 6
    argDict[ 'nodes' ]          = [ "a", "b", "c" ]

    cursor   = self.set_up_test( test_id, argDict )
    provTree = self.get_prov_tree( serial_nodes_path, \
                                   serial_edges_path, \
                                   argDict, \
                                   cursor )
    provTree.create_pydot_graph( 0, 0, test_id )

  ###############
  #  PATH LINK  #
  ###############
  #@unittest.skip( "works." )
  def test_path_link( self ) :

    test_id        = "path_link"
    test_file_name = "path_link"

    print " >>> RUNNING " + test_id + " <<<"

    test_id           = "combo_sip_" + test_id
    serial_nodes_path = "./testFiles/" + test_id + "_expected_nodes.txt"
    serial_edges_path = "./testFiles/" + test_id + "_expected_edges.txt"

    input_file                  = "./testFiles/" + test_file_name + ".ded"
    argDict                     = self.getArgDict( input_file )
    argDict[ 'data_save_path' ] = "./data/" + test_id + "/"
    argDict[ 'EOT' ]            = 1
    argDict[ 'nodes' ]          = [ "a" ]

    cursor   = self.set_up_test( test_id, argDict )
    provTree = self.get_prov_tree( serial_nodes_path, \
                                   serial_edges_path, \
                                   argDict, \
                                   cursor )
    provTree.create_pydot_graph( 0, 0, test_id )

  ###################
  #  GET PROV TREE  #
  ###################
  def get_prov_tree( self, serial_nodes_path, serial_edges_path, argDict, cursor ) :

    if not os.path.exists( argDict[ "data_save_path" ] ) :
      os.system( "mkdir " + argDict[ "data_save_path" ] )

    # --------------------------------------------------------------- #
    # convert dedalus into c4 datalog and evaluate

    parsedResults = self.get_program_results( argDict, cursor )

    # --------------------------------------------------------------- #
    # build provenance tree

    provTree = ProvTree.ProvTree( rootname       = "FinalState", \
                                  parsedResults  = parsedResults, \
                                  cursor         = cursor, \
                                  treeType       = "goal", \
                                  isNeg          = False, \
                                  eot            = argDict[ "EOT" ], \
                                  prev_prov_recs = {}, \
                                  argDict        = argDict )

    # get actual serialized graph
    if serial_nodes_path :
      actual_serial_nodes = provTree.nodeset_pydot_str
    if serial_edges_path :
      actual_serial_edges = provTree.edgeset_pydot_str

    if self.PRINT_STOP :

      if serial_nodes_path :
        for n in actual_serial_nodes :
          logging.debug( "  n = " + n.rstrip() )

      if serial_nodes_path :
        for e in actual_serial_edges :
          logging.debug( "  e = " + e.rstrip() )

      tools.bp( __name__, inspect.stack()[0][3], "print stop." )

    return provTree


  #########################
  #  GET PROGRAM RESULTS  #
  #########################
  # convert the input dedalus program into c4 datalog and evaluate.
  # return evaluation results dictionary.
  def get_program_results( self, argDict, cursor ) :

    # convert dedalus into c4 datalog
    allProgramData = dedt.translateDedalus( argDict, cursor )

    # run c4 evaluation
    results_array = c4_evaluator.runC4_wrapper( allProgramData[0], argDict )
    parsedResults = tools.getEvalResults_dict_c4( results_array )

    return parsedResults


  #################
  #  SET UP TEST  #
  #################
  def set_up_test( self, test_id, argDict ) :

    if os.path.exists( "./IR_" + test_id + ".db*" ) :
      os.remove( "./IR*.db*" )

    testDB = "./IR_" + test_id + ".db"
    IRDB   = sqlite3.connect( testDB )
    cursor = IRDB.cursor()

    dedt.createDedalusIRTables(cursor)
    dedt.globalCounterReset()

    return cursor


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
    argDict[ 'settings' ]                 = "./settings_combo_sip.ini"
    argDict[ 'negative_support' ]         = False
    argDict[ 'strategy' ]                 = None
    argDict[ 'file' ]                     = inputfile
    argDict[ 'EOT' ]                      = 4
    argDict[ 'find_all_counterexamples' ] = False
    argDict[ 'nodes' ]                    = [ "a", "b", "c" ]
    argDict[ 'evaluator' ]                = "c4"
    argDict[ 'EFF' ]                      = 2
    argDict[ 'data_save_path' ]           = "./data/"
    argDict[ 'neg_writes' ]               = "combo"

    return argDict


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
if __name__ == "__main__":
  unittest.main()

#########
#  EOF  #
#########
