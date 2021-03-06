#!/usr/bin/env python

'''
Core.py
'''

# **************************************** #


#############
#  IMPORTS  #
#############
# standard python packages
import inspect, itertools, logging, os, sqlite3, string, sys, time

# ------------------------------------------------------ #
# import sibling packages HERE!!!
if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from dedt           import dedt, dedalusParser
from utils          import parseCommandLineInput, tools
from evaluators     import c4_evaluator

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../.." ) )

from derivation     import ProvTree

# **************************************** #


####################
#  CLASS LDFICORE  #
####################
class Core :

  # --------------------------------- #
  #############
  #  ATTRIBS  #
  #############
  argDict                  = None  # dictionary of commaned line args
  cursor                   = None  # a reference to the IR database

  # --------------------------------- #

  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, argDict, cursor ) :
    self.argDict             = argDict
    self.cursor              = cursor


  ##################
  #  RUN WORKFLOW  #
  ##################
  def run_workflow( self ) :

    logging.debug( "*******************************************************" )
    logging.debug( "                   RUNNING ORIK CORE" )
    logging.debug( "*******************************************************" )

    # ---------------------------------------------------------------- #
    # 1. build c4 datalog program (USING IAPYX)                        #
    # ---------------------------------------------------------------- #

    # allProgramData := [ allProgramLines, tableListArray ]
    allProgramData = self.dedalus_to_datalog( self.argDict, self.cursor )
    program_lines  = allProgramData[0]
    table_array    = allProgramData[1]

    # ----------------------------------------------- #
    # 2. evaluate (USING IAPYX)                       #
    # ----------------------------------------------- #

    # use c4 wrapper always 
    parsedResults = self.evaluate( self.argDict, allProgramData )

    # ---------------------------------------------------- #
    # 3. get provenance tree (THIS IS THE ORIK STUFF)      #
    # ---------------------------------------------------- #

    provTreeComplete = self.buildProvTree( parsedResults, self.argDict[ "EOT" ], 0, self.cursor )


  ########################
  #  DEDALUS TO DATALOG  #
  ########################
  # translate all input dedalus files into a single datalog program
  def dedalus_to_datalog( self, argDict, cursor ) :
    return dedt.translateDedalus( argDict, cursor )
  
  
  ##############
  #  EVALUATE  #
  ##############
  # evaluate the datalog program using some datalog evaluator
  # return some data structure or storage location encompassing the evaluation results.
  def evaluate( self, argDict, allProgramData ) :

    # ----------------------------------------------------------------- #
    # inject custom faults here.

    allProgramData = self.injectCustomFaults( argDict, allProgramData )

    # ----------------------------------------------------------------- #
    # run the program evaluation using c4

    results_array = c4_evaluator.runC4_wrapper( allProgramData )

    # ----------------------------------------------------------------- #
    # dump evaluation results locally

    eval_results_dump_dir = os.path.abspath( os.getcwd() ) + "/data/"

    # make sure data dump directory exists
    if not os.path.isdir( eval_results_dump_dir ) :

      logging.debug( "WARNING : evalulation results file dump destination does not exist at " + eval_results_dump_dir )
      logging.debug( "> creating data directory at : " + eval_results_dump_dir )

      os.system( "mkdir " + eval_results_dump_dir )

      if not os.path.isdir( eval_results_dump_dir ) :
        tools.bp( __name__, inspect.stack()[0][3], "FATAL ERROR : unable to create evaluation \
                                                                  results dump directory at " + \
                                                                  eval_results_dump_dir )
      logging.debug( "...done." )

    # ----------------------------------------------------------------- #
    # data dump directory exists by now, so perform the dump.

    self.eval_results_dump_to_file( results_array, eval_results_dump_dir )

    # ----------------------------------------------------------------- #
    # parse results into a dictionary

    parsedResults = tools.getEvalResults_dict_c4( results_array )

    # ----------------------------------------------------------------- #

    return parsedResults

 
  ###############################
  #  EVAL RESULTS DUMP TO FILE  #
  ###############################
  def eval_results_dump_to_file( self, results_array, eval_results_dump_dir ) :

    logging.debug( "  EVAL RESULTS DUMP TO FILE : running process..." )

    eval_results_dump_file_path = eval_results_dump_dir + "eval_dump_0.txt"

    # save new contents
    f = open( eval_results_dump_file_path, "w" )

    for line in results_array :
      
      # output to stdout
      logging.debug( "line = " + str( line ) )

      # output to file
      f.write( line + "\n" )

    f.close()
 
  
  #####################
  #  BUILD PROV TREE  #
  #####################
  # use the evaluation execution results to build a provenance tree of the evaluation execution.
  # return a provenance tree instance
  def buildProvTree( self, parsedResults, eot, iter_count, irCursor ) :
  
    logging.debug( "  BUILD PROV TREE : running process..." )

    # build provenance tree structure
    provTreeComplete = ProvTree.ProvTree( rootname      = "FinalState", \
                                          parsedResults = parsedResults, \
                                          cursor        = irCursor, \
                                          treeType      = "goal", \
                                          isNeg         = False, \
                                          eot           = eot, \
                                          argDict       = self.argDict )

    # ------------------------------------------------------------------------------ #
    # build the provenance graph

    default_fmla_index = 0 
    provTreeComplete.create_pydot_graph( default_fmla_index, iter_count, None )

    # ------------------------------------------------------------------------------ #

    return provTreeComplete
  
 
  ##########################
  #  INJECT CUSTOM FAULTS  #
  ##########################
  # example :
  #   [CORE]
  #   CUSTOM_FAULT = ['clock("str","str",2,2)']
  # use double quotes for str data in clock tuples and single quotes around clock facts.
  
  def injectCustomFaults( self, argDict, allProgramData ) :
  
    # grab the custom fault, which is a list of clock fact strings, with quotes,
    # to remove from full clock relation
    customFaultList = tools.getConfig( argDict[ "settings" ], "CORE", "CUSTOM_FAULT", list )
  
    if customFaultList :
      # delete specified clock facts from program
      faultyProgramLines = []
      programLines       = allProgramData[0]
      tableList          = allProgramData[1]
      for line in programLines :
        line = line.replace( ";", "" )
        if line in customFaultList :
          pass
        else :
          faultyProgramLines.append( line + ";" )
  
      return [ faultyProgramLines, tableList ]
  
    else :
      return allProgramData
 
#########
#  EOF  #
#########
