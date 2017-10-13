#!/usr/bin/env python

'''
unit_tests.py
'''

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sqlite3, sys, unittest
from StringIO import StringIO

# ------------------------------------------------------ #
# import sibling packages HERE!!!
sys.path.append( os.path.abspath( __file__ + "/../../../../src" ) )

from dedt  import dedt, dedalusParser, clockRelation, dedalusRewriter
from utils import tools

# ------------------------------------------------------ #


###################
#  TEST DEDT DEV  #
###################
class Test_dedt_dev( unittest.TestCase ) :

  ###############
  #  EXAMPLE 6  #
  ###############
  # example 6 details a correct program.
  # make sure this test produces the expected olg program.
  def test_example6( self ) :

    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()

    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes with expected error

    # specify input file path
    inputfile = "./testFiles/example6.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    try :
      programData = dedt.translateDedalus( argDict, cursor )
      # portray actual output program lines as a single string
      actual_results = self.getActualResults( programData[0][0] )

    # something broke. save output as a single string
    except :
      actual_results = self.getError( sys.exc_info() )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example6.olg"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "actual_results  :" + repr( actual_results )
    print "expected_results:" + repr( expected_results )

    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 5  #
  ###############
  # example 5 details an erroneous program.
  # make sure this test produces the expected error message.
  def test_example5( self ) :

    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()

    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes with expected error

    # specify input file path
    inputfile = "./testFiles/example5.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    try :
      programData = dedt.translateDedalus( argDict, cursor )
      # portray actual output program lines as a single string
      actual_results = self.getActualResults( programData[0][0] )

    # something broke. save output as a single string
    except :
      actual_results = self.getError( sys.exc_info() )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example5_error.txt"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "actual_results  :" + repr( actual_results )
    print "expected_results:" + repr( expected_results )

    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 4  #
  ###############
  # example 4 details an erroneous program.
  # make sure this test produces the expected error message.
  def test_example4( self ) :

    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()

    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes with expected error

    # specify input file path
    inputfile = "./testFiles/example4.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    try :
      programData = dedt.translateDedalus( argDict, cursor )
      # portray actual output program lines as a single string
      actual_results = self.getActualResults( programData[0][0] )

    # something broke. save output as a single string
    except :
      actual_results = self.getError( sys.exc_info() )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example4_error.txt"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "actual_results  :" + repr( actual_results )
    print "expected_results:" + repr( expected_results )

    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 3  #
  ###############
  # example 3 details an erroneous program.
  # make sure this test produces the expected error message.
  def test_example3( self ) :
 
    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()
 
    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes with expected error

    # specify input file path
    inputfile = "./testFiles/example3.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    try :
      programData = dedt.translateDedalus( argDict, cursor )
      # portray actual output program lines as a single string
      actual_results = self.getActualResults( programData[0][0] )

    # something broke. save output as a single string
    except :
      actual_results = self.getError( sys.exc_info() )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example3_error.txt"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()
   
    print "actual_results  :" + repr( actual_results )
    print "expected_results:" + repr( expected_results )

    self.assertEqual( actual_results, expected_results )
    
    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )

  ###############
  #  EXAMPLE 2  #
  ###############
  # example 2 details an erroneous program.
  # make sure this test produces the expected error message.
  def test_example2( self ) :
 
    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()
 
    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes with expected error

    # specify input file path
    inputfile = "./testFiles/example2.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    try :
      programData = dedt.translateDedalus( argDict, cursor )
      # portray actual output program lines as a single string
      actual_results = self.getActualResults( programData[0][0] )

    # something broke. save output as a single string
    except :
      actual_results = self.getError( sys.exc_info() )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example2_error.txt"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()
   
    print "actual_results  :" + repr( actual_results )
    print "expected_results:" + repr( expected_results )

    self.assertEqual( actual_results, expected_results )
    
    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###############
  #  EXAMPLE 1  #
  ###############
  def test_example1( self ) :
  
    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()
  
    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes without error

    # specify input file path
    inputfile = "./testFiles/example1.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    programData = dedt.translateDedalus( argDict, cursor )

    # portray actual output program lines as a single string
    actual_results = self.getActualResults( programData[0][0] )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example1.olg"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "expected_results:" + str( expected_results )
    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###################
  #  EXAMPLE EMPTY  #
  ###################
  def test_example_empty( self ) :

    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()

    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes without error

    # specify input file path
    inputfile = "./testFiles/example_empty.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    programData = dedt.translateDedalus( argDict, cursor )

    # portray actual output program lines as a single string
    actual_results = self.getActualResults( programData[0][0] )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example_empty.olg"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "expected_results:" + str( expected_results )
    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  #################################
  #  EXAMPLE EMPTY WITH COMMENTS  #
  #################################
  def test_example_empty_with_comments( self ) :

    # --------------------------------------------------------------- #
    #testing set up. dedToIR has dependency
    #on createDedalusIRTables so that's
    #tested first above.
    testDB = "./IR.db"
    IRDB    = sqlite3.connect( testDB )
    cursor  = IRDB.cursor()

    # --------------------------------------------------------------- #
    #dependency
    dedt.createDedalusIRTables(cursor)

    # --------------------------------------------------------------- #
    #runs through function to make sure it finishes without error

    # specify input file path
    inputfile = "./testFiles/example_empty_with_comments.ded"

    # get argDict
    argDict = self.getArgDict( inputfile )

    # run translator
    programData = dedt.translateDedalus( argDict, cursor )

    # portray actual output program lines as a single string
    actual_results = self.getActualResults( programData[0][0] )

    # grab expected output results as a string
    expected_results_path = "./testFiles/example_empty_with_comments.olg"
    expected_results      = None
    with open( expected_results_path, 'r' ) as expectedFile :
      expected_results = expectedFile.read()

    print "expected_results:" + str( expected_results )
    self.assertEqual( actual_results, expected_results )

    # --------------------------------------------------------------- #
    #clean up testing
    IRDB.close()
    os.remove( testDB )


  ###############
  #  GET ERROR  #
  ###############
  # extract error message from system info
  def getError( self, sysInfo ) :
    return str( sysInfo[1] )


  ########################
  #  GET ACTUAL RESULTS  #
  ########################
  def getActualResults( self, programLines ) :
    program_string  = "\n".join( programLines )
    program_string += "\n" # add extra newline to align with read() parsing
    return program_string


  ##################
  #  GET ARG DICT  #
  ##################
  def getArgDict( self, inputfile ) :

    # initialize
    argDict = {}

    # populate with unit test defaults
    argDict[ 'prov_diagrams' ]            = False
    argDict[ 'use_symmetry' ]             = False
    argDict[ 'crashes' ]                  = 0
    argDict[ 'solver' ]                   = None
    argDict[ 'disable_dot_rendering' ]    = False
    argDict[ 'settings' ]                 = "./testFile/settings.ini"
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
